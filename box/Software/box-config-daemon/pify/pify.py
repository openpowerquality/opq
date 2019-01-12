import logging
import sched
import subprocess
import sys
import time
import threading
import typing

import conf
import nmoperations
import web.server

logging.basicConfig(level=logging.DEBUG)

def open_port_80_wlan0():
    logging.info("Opening port 80 on wlan0")
    subprocess.run(["/sbin/iptables", "-D", "INPUT", "-p", "tcp", "-i", "wlan0", "--dport", "80", "-j",  "REJECT"])

def close_port_80_wlan0():
    logging.info("Closing port 80 on wlan0")
    subprocess.run(["/sbin/iptables", "-A", "INPUT", "-p", "tcp", "-i", "wlan0", "--dport", "80", "-j",  "REJECT"])

def fsm_start(nm: nmoperations.NM):
    disable_ap(nm)
    #nm.get_ssids()
    fsm_is_conn_a(nm)


def fsm_is_conn_a(nm: nmoperations.NM):
    if nm.is_connected_to_internet():
        logging.info("is_conn_a: connected to internet, monitoring connection")
        fsm_monitor_connection(nm)
    else:
        logging.info("is_conn_a: not connected to internet, attempting to connect to any open network")
        fsm_connect_any(nm)


def fsm_is_conn_b(nm: nmoperations.NM):
    if nm.is_connected_to_internet():
        logging.info("is_conn_b: connected to internet, monitoring connection")
        fsm_monitor_connection(nm)
    else:
        logging.info("is_conn_b: not connected to internet, going into AP mode")
        enable_ap(nm)


def fsm_connect_any(nm: nmoperations.NM):
    disable_ap(nm)
    logging.info("Attempting to connect to any open or previously connected networks")
    nm.activate_any_connection()
    logging.info("After connect any")
    wait_then_run(10, fsm_is_conn_b, [nm], True)


def fsm_monitor_connection(nm: nmoperations.NM):
    if nm.is_connected_to_internet():
        logging.info("monitor_connection: connected to internet")
        wait_then_run(60, fsm_monitor_connection, [nm], blocking=True)
    else:
        logging.info("monitor_connection: not connected to internet")
        enable_ap(nm)


def fsm_monitor_ap(nm: nmoperations.NM):
    logging.info("monitor_ap")
    disable_ap(nm)
    #nm.get_ssids()
    fsm_is_conn_a(nm)


def enable_ap(nm: nmoperations.NM):
    while not nm.is_in_AP_mode():
        logging.info("Attempting to go into AP mode")
        nm.create_AP()
        time.sleep(1)

    open_port_80_wlan0()
    wait_then_run(60 * 10, fsm_monitor_ap, [nm])


def disable_ap(nm: nmoperations.NM):
    while nm.is_in_AP_mode():
        logging.info("Disabling AP mode")
        nm.disable_AP_mode()
        time.sleep(1)

    close_port_80_wlan0()
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


def refresh(nm: nmoperations.NM):
    logging.info("refresh")
    disable_ap(nm)
    time.sleep(5)
    enable_ap(nm)
    logging.info("refresh done")


def forget_networks(nm: nmoperations.NM):
    logging.info("Forgetting all wireless networks")
    disable_ap(nm)
    nm.delete_all_connection()
    enable_ap(nm)


def wait_then_run(sec: int, fn: typing.Callable, args: typing.List, blocking: bool = False):
    s = sched.scheduler()
    s.enter(sec, 1, fn, tuple(args))
    s.run(blocking=blocking)


class PifyFsmThread(threading.Thread):
    def __init__(self, nm):
        super().__init__()
        self.nm = nm

    def run(self):
        fsm_start(self.nm)

    def nm(self):
        return self.nm


if __name__ == "__main__":
    logging.info("Starting pify")

    # Check if config file is being passed at startup
    if len(sys.argv) == 2:
        path = sys.argv[1]
        logging.info("Loading configuration from {}".format(path))
        config = conf.PifyConfiguration(path)
    else:
        logging.info("Loading default configuration")
        config = conf.PifyConfiguration()

    logging.debug("Configuration is:\n{}".format(str(config)))

    # Grab an instance of the network manager, it is thread safe
    nm = nmoperations.NM(config)

    logging.info("Starting pify FSM")
    fsm_thread = PifyFsmThread(nm)
    fsm_thread.start()

    logging.info("Starting bottle server")
    web.server.run(config, nm)
