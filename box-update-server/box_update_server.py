"""
This module provides a pure Python HTTP server that acts as an OPQBox update server.
"""

import glob
import http.server
import json
import logging
import os
import os.path
import time
import typing

logging.basicConfig(level=logging.INFO)

BOX_UPDATE_SERVER_SETTINGS = "BOX_UPDATE_SERVER_SETTINGS"


def request_handler_factory(update_dir: str):
    """
    This factory creates a closure around the provided update directory.
    :param update_dir: The directory containing OPQBox updates.
    :return: An instance of a BoxUpdateServerHandler
    """

    def enumerate_updates() -> typing.List[str]:
        """
        Returns a list of available OPQBox updates.
        :return: A list of available OPQBox updates.
        """
        pattern = update_dir + "/opq-box-update-*.tar.bz2"
        update_packages = glob.glob(pattern)
        return sorted(update_packages)

    def version() -> typing.Optional[int]:
        """
        Returns the latest version of available OPQBox updates.
        :return: The latest version of available OPQBox updates.
        """
        updates = enumerate_updates()
        if len(updates) == 0:
            return None

        def extract_version(path: str) -> int:
            """
            Extracts the version number of an OPQBox update from a path to the update file.
            :param path: Path to update file.
            :return: The version number which represents a timestamp in epoch milliseconds.
            """
            file_name = path.split("/")[-1]
            sans_ext = file_name.split(".")[0]
            return int(sans_ext.split("-")[-1])

        versions = list(map(extract_version, updates))
        return versions[-1]

    class BoxUpdateServerHandler(http.server.BaseHTTPRequestHandler):
        """
        This class acts as a request handler for any HTTP requests received by the OPQBox update server.
        """

        def resp_plain_text(self, msg: str, code: int = 200):
            """
            Respond with plain text.
            :param msg: The message to respond with.
            :param code: The HTTP status code.
            """
            self.send_response(code)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))

        def resp_json(self, msg: typing.Dict, code: int = 200):
            """
            Respond with json.
            :param msg: A dictionary message to be serialized to json.
            :param code: The HTTP status code (default 200).
            """
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(msg).encode("utf-8"))

        def resp_file(self, file_path: str):
            """
            Respond with a file.
            :param file_path: Path to the file to respond with.
            """
            if not os.path.isfile(file_path):
                self.resp_plain_text("Resource not found.", 404)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header('Content-Disposition', 'attachment; filename="%s"' % file_path.split("/")[-1])
                self.send_header("Content-Length", os.path.getsize(file_path))
                self.end_headers()
                with open(file_path, "rb") as fin:
                    self.wfile.write(fin.read())

        def resp_redirect(self, location: str):
            """
            Respond with a redirect.
            :param location: Redirect to this location.
            """
            self.send_response(303)
            self.send_header("Location", location)
            self.end_headers()

        def handle_version(self):
            """
            Respond with most recent version of an OPQBox update.
            """
            version_num = version()
            if version_num is not None:
                self.resp_plain_text(str(version_num))
            else:
                self.resp_plain_text("Update dir does not contain any valid updates.", 404)

        def handle_ls(self):
            """
            Respond with a list of available OPQbox updates.
            """
            updates = enumerate_updates()
            self.resp_plain_text("\n".join(map(lambda path: path.split("/")[-1], updates)))

        def handle_get_update(self, update: str):
            """
            Respond with the specified OPQBox update file.
            :param update: The update to retrieve.
            """
            self.resp_file(update_dir + "/" + update)

        def handle_latest(self):
            """
            Respond by redirecting to the latest update (if it exists).
            """
            updates = enumerate_updates()
            if len(updates) == 0:
                self.resp_plain_text("Resource not found.", 404)
            else:
                self.resp_redirect("/update/%s" % updates[-1].split("/")[-1])

        # pylint: disable=C0103
        def do_GET(self):
            """
            Specify HTTP routes.
            """
            path: str = self.path
            if path == "/":
                self.resp_json({
                    "name": "Box Update Server",
                    "ok": True,
                    "timestamp": int(time.time()),
                    "subcomponents": []
                })
            elif path == "/ls":
                self.handle_ls()
            elif path == "/version":
                self.handle_version()
            elif path == "/latest":
                self.handle_latest()
            elif path.startswith("/update/"):
                self.handle_get_update(path.split("/")[-1])
            else:
                self.resp_plain_text("Resource not found.", 404)

    return BoxUpdateServerHandler


def usage():
    """
    Logs the usage of this server.
    """
    logging.info("usage: python3 box_update_server.py")


if __name__ == "__main__":
    """
    Entry point.
    """
    import sys

    config = os.environ.get(BOX_UPDATE_SERVER_SETTINGS)
    if config is None or len(config) == 0:
        logging.error("Config could not be loaded from the environment @ %s.", BOX_UPDATE_SERVER_SETTINGS)
        sys.exit(1)

    PORT: int = config["port"]
    UPDATE_DIR: str = config["updates_dir"]

    if not os.path.isdir(UPDATE_DIR):
        logging.warning("Update directory does not exist!")
        usage()
        sys.exit(1)

    logging.info("Starting box-update-server")
    HTTPD = http.server.HTTPServer(("", PORT), request_handler_factory(UPDATE_DIR))

    try:
        HTTPD.serve_forever()
    except KeyboardInterrupt:
        pass

    HTTPD.server_close()
    logging.info("Exiting box-update-server")
