import argparse
import http.server
import json
import math

SQRT_2 = math.sqrt(2)


class WaveformGenerator:
    def __init__(self):
        self.amplitude = 120.0 * SQRT_2
        self.frequency = 60.0
        self.phase = 0.0
        self.sample_rate_hz = 12000.0
        self.samples_per_cycle = 200
        self.generator = self.waveform_gen()
        self.cur_i = None

    def waveform_gen(self, start: int = 0):
        i = start
        while True:
            yield (i, self.amplitude * math.sin(self.frequency * (2 * math.pi) * i / self.sample_rate_hz))
            if i == self.samples_per_cycle - 1:
                i = 0
            else:
                i += 1

    def next(self):
        self.cur_i, v = next(self.generator)
        return v


class SimRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def _set_headers(self, resp: int):
        self.send_response(resp)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        print(self.path)
        self._set_headers(200)
        # self.send_response(200)
        self.wfile.write(json.dumps({"error": "Please POST requests"}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data_dict = json.loads(post_data)
        print(data_dict)
        self._set_headers(200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("sim.py",
                                     "python3 sim.py",
                                     "Box simulator server")
    parser.add_argument("--port", "-p",
                        type=int,
                        default=8000,
                        help="Specified port number to serve from")
    args = parser.parse_args()

    httpd = http.server.HTTPServer(("", args.port), SimRequestHandler)

    try:
        print("Starting opq-sim server on port {}...".format(args.port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Stopping opq-sim server... ", end="")
    httpd.server_close()
    print("Done.")
