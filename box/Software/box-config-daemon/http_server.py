"""
This module provides a barebone HTTP interface for managing an OPQ Box configuration and WiFi connection.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

# import pify.pify
import threading

logging.basicConfig(level=logging.DEBUG)


def opq_request_handler_factory(config_path, nm):
    """
    This method returns an BaseHTTPRequestHandler while wrapping a config path and network manager within a closure.
    for access within the handler.
    :param config_path: Path to configuration file.
    :param nm: Network manager.
    :return: A custom HTTP request handler.
    """
    def read_config():
        with open(config_path, "r") as fin:
            return json.load(fin)

    def write_config(config):
        with open(config_path, "w") as fout:
            json.dump(config, fout, indent=2)

    class OpqRequestHandler(BaseHTTPRequestHandler):
        """
        This class provides the functionality required for an HTTP server supporting GET and POST requests.
        This server can serve HTML, JSON, ICO, and plain text.
        """

        def respond(self, msg, code=200, content_type="text/plain", transform=None, utf8_encode=True):
            """
            Responds to the HTTP request.
            :param msg: A generic message.
            :param code: HTTP response code.
            :param content_type: Type of msg.
            :param transform: A function to convert the msg from one type to another.
            :param utf8_encode: Should the resulting message be UTF-8 encoded or not.
            """
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.end_headers()

            if transform is not None:
                if utf8_encode:
                    self.wfile.write(transform(msg).encode("utf-8"))
                else:
                    self.wfile.write(transform(msg))
            else:
                if utf8_encode:
                    self.wfile.write(msg.encode("utf-8"))
                else:
                    self.wfile.write(msg)

        def html(self, msg):
            """
            Respond with HTML.
            :param msg: The HTML message.
            """
            self.respond(msg, content_type="text/html")

        def json(self, msg):
            """
            Respond with JSON.
            :param msg: The message to be serielized into JSON
            """
            self.respond(msg, content_type="application/json", transform=json.dumps)

        def ico(self, msg):
            """
            Responds with an icon msg.
            :param msg: An icon (raw bytes)
            """
            self.respond(msg, content_type="image/vnd.microsoft.icon", utf8_encode=False)

        def error(self, msg, code=500, ex=None):
            """
            Respond with an error message.
            :param msg: The message to include in the error (will be serielized to JSON)
            :param code: The HTTP error code
            :param ex: The optional original exception that occurred on the server for logging
            """
            self.respond({"error": msg}, code=code, content_type="application/json", transform=json.dumps)
            if ex is not None:
                logging.error("Error: %s\n%s\n" % (msg, str(ex)))

        def not_found(self, path):
            """
            Provided path not found on this server
            :param path: Path that was not found
            """
            self.error("Path [%s] not found" % path, code=404)

        def do_GET(self):
            """
            Handler for HTTP GET requests.
            The path is extracted from the request and then matched to perform the corresponding action.
            """
            path = self.path
            if path == "/":
                with open("box-config-daemon.html") as fin:
                    self.html(fin.read())
            elif path == "/box_config":
                try:
                    self.json({"box_config": read_config()})
                except Exception as e:
                    self.error("Unable to read box config", ex=e)
            elif path == "/ssids":
                try:
                    ssid_name_set = set()
                    ssid_results = []
                    ssids = nm.get_ssids()
                    for ssid in ssids:
                        ssid[0] = ssid[0].decode("utf-8")
                        if ssid[0] not in ssid_name_set:
                            ssid_name_set.add(ssid[0])
                            ssid_results.append(ssid)

                    self.json({"ssids": ssid_results})
                except Exception as e:
                    self.error("Unable to retrieve SSID list", ex=e)
            elif path == "/opq.ico":
                try:
                    with(open("opq.ico", "rb")) as fin:
                        self.ico(fin.read())
                except Exception as e:
                    self.error("Unable to read icon file", ex=e)
            else:
                self.not_found("GET %s" % path)

        def do_POST(self):
            """
            Handler for HTTP post requests. All data is assumed to be JSON.
            :return:
            """
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode())

            path = self.path
            if path == "/connect":
                try:
                    ssid = post_data["ssid"]
                    password = post_data["password"]
                    if password is None or len(password) == 0:
                        timer = threading.Timer(5, pify.pify.connect_open, (nm, ssid))
                        timer.start()
                        self.json({"status": "Attempting to connect to %s" % ssid})
                    else:
                        timer = threading.Timer(5, pify.pify.connect_wpa, (nm, ssid, password))
                        timer.start()
                        self.json({"status": "Attempting to connect OPQ Box to %s. If the connection is successful, this device will drop the OPQ connection and reconnect to the previously connected network. If the connection is unsuccessful, the OPQ Box will go back into AP mode and the OPQ network will reappear to attempt to setup the connection again." % ssid})
                except Exception as e:
                    self.error("Could not connect to WiFi access point", ex=e)
            elif path == "/box_config":
                try:
                    box_config = post_data["box_config"]
                    write_config(json.loads(box_config))
                    self.json({"status": "OPQ Box configuration updated."})
                except Exception as e:
                    self.error("Could not update server_public_key", ex=e)
            else:
                self.not_found("POST [%s]" % path)

    return OpqRequestHandler


def run_server(port, config_file, nm):
    """
    Starts the http server.
    :param port: Port to run server on.
    :param config_file: Path to configuration file.
    :param nm: Instance of nmoperations.
    """
    logging.info("Starting box-config-daemon server on port %d with config %s" % (port, config_file))
    httpd = HTTPServer(("", port), opq_request_handler_factory(config_file, nm))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Exiting box-config-daemon server")
