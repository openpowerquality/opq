import logging
import sched
import time
import threading
import typing

import opq_display.opq_display_client as display_client
import pify.nmoperations as nmoperations

logging.basicConfig(level=logging.DEBUG)


def fsm_start(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    disable_ap(nm)
    fsm_is_conn_a(nm, disp_client)


def fsm_is_conn_a(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    if nm.is_connected_to_internet():
        logging.info("is_conn_a: connected to internet, monitoring connection")
        fsm_monitor_connection(nm, disp_client)
    else:
        logging.info("is_conn_a: not connected to internet, attempting to connect to any open network")
        fsm_connect_any(nm)


def fsm_is_conn_b(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    if nm.is_connected_to_internet():
        logging.info("is_conn_b: connected to internet, monitoring connection")
        fsm_monitor_connection(nm, disp_client)
    else:
        logging.info("is_conn_b: not connected to internet, going into AP mode")
        enable_ap(nm, disp_client)


def fsm_connect_any(nm: nmoperations.NM):
    disable_ap(nm)
    logging.info("Attempting to connect to any open or previously connected networks")
    nm.activate_any_connection()
    logging.info("After connect any")
    wait_then_run(10, fsm_is_conn_b, [nm], True)


def fsm_monitor_connection(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    if nm.is_connected_to_internet():
        logging.info("monitor_connection: connected to internet")
        # Update display to scroll through normal screens.
        disp_client.send_display_normal_cmd()
        wait_then_run(60, fsm_monitor_connection, [nm], blocking=True)
    else:
        logging.info("monitor_connection: not connected to internet")
        enable_ap(nm, disp_client)


def fsm_monitor_ap(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    logging.info("monitor_ap")
    disable_ap(nm)
    fsm_is_conn_a(nm, disp_client)


def enable_ap(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    while not nm.is_in_AP_mode():
        logging.info("Attempting to go into AP mode")
        nm.create_AP()
        time.sleep(1)

    # AP mode enabled, update display status.
    disp_client.send_display_ap_cmd()
    wait_then_run(60 * 10, fsm_monitor_ap, [nm])


def disable_ap(nm: nmoperations.NM):
    while nm.is_in_AP_mode():
        logging.info("Disabling AP mode")
        nm.disable_AP_mode()
        time.sleep(1)

    logging.info("AP mode disabled")


def connect_open(nm: nmoperations.NM, ssid: str):
    logging.info("connect_open")
    disable_ap(nm)
    nm.add_connection_open(ssid)
    nm.activate_connection(ssid)
    wait_then_run(5, fsm_monitor_connection, [nm])


def connect_wpa(nm: nmoperations.NM, ssid: str, passwd: str):
    logging.info("connect_wpa")
    disable_ap(nm)
    nm.add_connection_wpa(ssid, passwd)
    nm.activate_connection(ssid)
    wait_then_run(5, fsm_monitor_connection, [nm])


def refresh(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    logging.info("refresh")
    disable_ap(nm)
    time.sleep(5)
    enable_ap(nm, disp_client)
    logging.info("refresh done")


def forget_networks(nm: nmoperations.NM, disp_client: display_client.OpqDisplayClient):
    logging.info("Forgetting all wireless networks")
    disable_ap(nm)
    nm.delete_all_connection()
    enable_ap(nm, disp_client)


def wait_then_run(sec: int, fn: typing.Callable, args: typing.List, blocking: bool = False):
    s = sched.scheduler()
    s.enter(sec, 1, fn, tuple(args))
    s.run(blocking=blocking)


class PifyFsmThread(threading.Thread):
    def __init__(self,
                 nm: nmoperations.NM,
                 disp_client: display_client.OpqDisplayClient):
        super().__init__()
        self.nm = nm
        self.disp_client = disp_client

    def run(self):
        fsm_start(self.nm, self.disp_client)

    def nm(self) -> nmoperations.NM:
        return self.nm

    def disp_client(self) -> display_client.OpqDisplayClient:
        return self.disp_client
