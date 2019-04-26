import argparse
import logging
import os
import socket

import opq_display.display_types as display_types

logger = logging.getLogger("opq_display_client")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port",
                        type=int,
                        help="OPQ Display Server port")
    parser.add_argument("cmd",
                        type=str,
                        help="Command to send to OPQ Display Server",
                        choices=display_types.DISPLAY_TYPES)

    args = parser.parse_args()
    client = OpqDisplayClient(args.port)
    client.send_cmd(args.cmd)
