import argparse
import logging
import os
import socket

import display_types
import opq_display

logger = logging.getLogger("opq_display_server")
logging.basicConfig(
        format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))
logger.setLevel(logging.DEBUG)


class OpqDisplayClient:

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = ("127.0.0.1", port)

    def send_cmd(self, cmd):
        if not display_types.is_display_type(cmd):
            logger.error("Invalid cmd %s, valid commands are %s", cmd, display_types.DISPLAY_TYPES)
            return

        try:
            bytes_sent = self.sock.sendto(bytes(cmd), self.addr)
            logger.debug("Sent cmd %s with %d bytes to server at %s", cmd, bytes_sent, self.addr)
        except Exception as e:
            logger.error("Error sending command to server: %s", str(e))
        finally:
            self.sock.close()
            logger.debug("Client connection closed.")

    def send_display_splash_cmd(self):
        self.send_cmd(display_types.DISPLAY_SPLASH)

    def send_display_normal_cmd(self):
        self.send_cmd(display_types.DISPLAY_NORMAL)

    def send_display_ap_cmd(self):
        self.send_cmd(display_types.DISPLAY_AP)


def handle_cmd(opq_disp, cmd):
    if not display_types.is_display_type(cmd):
        logger.error("Invalid cmd %s, valid commands are %s", cmd, display_types.DISPLAY_TYPES)
        return

    if cmd == display_types.DISPLAY_SPLASH:
        opq_disp.display_opq_logo()
    elif cmd == display_types.DISPLAY_NORMAL:
        opq_disp.display_normal()
    elif cmd == display_types.DISPLAY_AP:
        opq_disp.display_ap_message()
    else:
        logger.error("Invalid cmd %s, valid commands are %s", cmd, display_types.DISPLAY_TYPES)


def start_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))

    logger.debug("Starting opq display server on port %d", port)
    buf_size = display_types.max_size()
    opq_disp = opq_display.OpqDisplay()
    opq_disp.display_opq_logo()
    while True:
        cmd = str(sock.recv(buf_size))
        if display_types.is_display_type(cmd):
            logger.debug("Received cmd %s", cmd)
            handle_cmd(opq_disp, cmd)
        else:
            logger.error("Received invalid display type %s. Only display types of %s are valid.",
                         cmd,
                         display_types.DISPLAY_TYPES)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_server = subparsers.add_parser("server",
                                          help="Starts the opq-display server")
    parser_server.add_argument("port", type=int, help="opq-display server port")

    parser_client = subparsers.add_parser("client",
                                          help="Starts a opq-display client")
    parser_client.add_argument("port", type=int, help="opq-display server port")
    parser_client.add_argument("cmd", help="cmd to send to display server")

    args = parser.parse_args()

    if "cmd" in args:
        port = args.port
        cmd = args.cmd
        client = OpqDisplayClient(port)
        client.send_cmd(cmd)
    else:
        port = args.port
        start_server(port)
