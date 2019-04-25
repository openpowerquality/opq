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
    parser.add_argument("port",
                        type=int,
                        help="Port the display server should run on.")
    args = parser.parse_args()
    start_server(args.port)
