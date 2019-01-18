import glob
import http.server
import logging
import os.path
import typing

logging.basicConfig(level=logging.INFO)


def request_handler_factory(update_dir: str):
    def enumerate_updates() -> typing.List[str]:
        pattern = update_dir + "/opq-box-update-*.tar.bz2"
        update_packages = glob.glob(pattern)
        sorted(update_packages)
        return update_packages

    def version() -> typing.Optional[int]:
        updates = enumerate_updates()
        if len(updates) == 0:
            return None

        def extract_version(path: str) -> int:
            file_name = path.split("/")[-1]
            sans_ext = file_name.split(".")[0]
            return int(sans_ext.split("-")[-1])

        versions = list(map(extract_version, updates))
        return versions[-1]


    class BoxUpdateServerHandler(http.server.BaseHTTPRequestHandler):
        def resp_plain_text(self, msg: str, code: int = 200):
            self.send_response(code)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))

        def resp_file(self, file_path: str):
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
            self.send_response(303)
            self.send_header("Location", location)
            self.end_headers()

        def handle_version(self):
            v = version()
            if v is not None:
                self.resp_plain_text(str(v))
            else:
                self.resp_plain_text("Update dir does not contain any valid updates.", 404)

        def handle_ls(self):
            updates = enumerate_updates()
            self.resp_plain_text("\n".join(map(lambda path: path.split("/")[-1], updates)))

        def handle_get_update(self, update):
            self.resp_file(update_dir + "/" + update)

        def handle_latest(self):
            updates = enumerate_updates()
            if len(updates) == 0:
                self.resp_plain_text("Resource not found.", 404)
            else:
                self.resp_redirect("/update/%s" % updates[-1].split("/")[-1])

        def do_GET(self):
            path: str = self.path
            if path == "/":
                self.resp_plain_text("")
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
    logging.info("usage: python3 box_update_server.py [port] [update directory]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        logging.warning("Incorrect number of args supplied.")
        usage()
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        logging.warning("Port is not a valid integer.")
        usage()
        sys.exit(1)

    update_dir = sys.argv[2]

    if not os.path.isdir(update_dir):
        logging.warning("Update directory does not exist!")
        usage()
        sys.exit(1)

    logging.info("Starting box-update-server")
    httpd = http.server.HTTPServer(("", port), request_handler_factory(update_dir))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    logging.info("Exiting box-update-server")
