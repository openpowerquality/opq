from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import pify.pify
import threading


def opq_request_handler_factory(config_path, nm):
    class OpqRequestHandler(BaseHTTPRequestHandler):

        def read_config(self):
            with open(config_path, "r") as fin:
                return json.load(fin)

        def write_config(self, config):
            with open(config_path, "w") as fout:
                json.dump(config, fout)

        def update_config(self, key, value):
            config = self.read_config()
            prev_value = config[key]
            config[key] = value
            self.write_config(config)
            return prev_value

        def respond(self, msg, code=200, content_type="text/plain", transform=None, utf8_encode=True):
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

        def css(self, msg):
            self.respond(msg, content_type="text/css")

        def html(self, msg):
            self.respond(msg, content_type="text/html")

        def json(self, msg):
            self.respond(msg, content_type="application/json", transform=json.dumps)

        def ico(self, msg):
            self.respond(msg, content_type="image/vnd.microsoft.icon", utf8_encode=False)

        def error(self, msg, code=500, ex=None):
            self.respond({"error": msg}, code=code, content_type="application/json", transform=json.dumps)
            if ex is not None:
                print("Error: %s\n%s\n" % (msg, str(ex)))

        def not_found(self, path):
            self.error("Path [%s] not found" % path, code=404)

        def do_GET(self):
            path = self.path
            if path == "/":
                with open("box-config-daemon.html") as fin:
                    self.html(fin.read())
            elif path == "/box_id":
                try:
                    self.json({"box_id": self.read_config()["box_id"]})
                except Exception as e:
                    self.error("Unable to read box_id", ex=e)
            elif path == "/triggering_endpoint":
                try:
                    self.json({"triggering_endpoint": self.read_config()["triggering_endpoint"]})
                except Exception as e:
                    self.error("Unable to read triggering_endpoint", ex=e)
            elif path == "/acquisition_endpoint":
                try:
                    self.json({"acquisition_endpoint": self.read_config()["acquisition_endpoint"]})
                except Exception as e:
                    self.error("Unable to read acquisition_endpoint", ex=e)
            elif path == "/updates_endpoint":
                try:
                    self.json({"updates_endpoint": self.read_config()["updates_endpoint"]})
                except Exception as e:
                    self.error("Unable to read updates_endpoint", ex=e)
            elif path == "/opq.ico":
                try:
                    with(open("opq.ico", "rb")) as fin:
                        self.ico(fin.read())
                except Exception as e:
                    self.error("Unable to read icon file", ex=e)
            elif path == "/ssids":
                try:
                    ssids = nm.get_ssids()
                    for ssid in ssids:
                        ssid[0] = ssid[0].decode("utf-8")
                    self.json({"ssids": ssids})

                    # self.json({"ssids": [["eduroam", 1, 70.0], ["UHM", 0, 72.0], ["mmrl", 1, 44.0]]})
                except Exception as e:
                    self.error("Unable to retrieve SSID list")
            elif path == "/public_key":
                pass
            else:
                # Return 404
                self.not_found("GET %s" % path)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode())

            path = self.path
            if path == "/box_id":
                try:
                    new_val = post_data["box_id"]
                    prev_val = self.update_config("box_id", new_val)
                    self.json({"status": "OPQ Box ID updated from %s to %s" % (prev_val, new_val)})
                except Exception as e:
                    self.error("Could not update box_id", ex=e)
            elif path == "/acquisition_endpoint":
                try:
                    new_val = post_data["acquisition_endpoint"]
                    prev_val = self.update_config("acquisition_endpoint", new_val)
                    self.json({"status": "OPQ Box Acquisition Endpoint updated from %s to %s" % (prev_val, new_val)})
                except Exception as e:
                    self.error("Could not update acquisition_endpoint", ex=e)
            elif path == "/triggering_endpoint":
                try:
                    new_val = post_data["triggering_endpoint"]
                    prev_val = self.update_config("triggering_endpoint", new_val)
                    self.json({"status": "OPQ Box Triggering Endpoint updated from %s to %s" % (prev_val, new_val)})
                except Exception as e:
                    self.error("Could not update triggering_endpoint", ex=e)
            elif path == "/updates_endpoint":
                try:
                    new_val = post_data["updates_endpoint"]
                    prev_val = self.update_config("updates_endpoint", new_val)
                    self.json({"status": "OPQ Box Updates Endpoint updated from %s to %s" % (prev_val, new_val)})
                except Exception as e:
                    self.error("Could not update updates_endpoint", ex=e)
            elif path == "/connect":
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
                        self.json({"status": "Attempting to connect to %s" % ssid})
                except Exception as e:
                    self.error("Could not connect to WiFi access point", ex=e)
            elif path == "/public_key":
                try:
                    pass
                except:
                    pass
            else:
                self.not_found("POST [%s]" % path)

    return OpqRequestHandler


def run_server(port, config_file, nm):
    print("Starting box-config-daemon server on port %d with config %s" % (port, config_file))
    httpd = HTTPServer(("", port), opq_request_handler_factory(config_file, nm))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Exiting box-config-daemon server")
