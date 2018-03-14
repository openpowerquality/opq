import argparse
import http.server
import json
import math
import multiprocessing
import time
import typing
import queue

SQRT_2 = math.sqrt(2)
S16_MIN = -(2 ** 15)
S16_MAX = 2 ** 15 - 1


def as_vrms(v: int, calibration_constant: float = 152.0) -> float:
    return (v / calibration_constant) / SQRT_2


def scale_to_sint16(v: float, calibration_constant: float = 152.0) -> int:
    r = round(v * calibration_constant)
    if r < S16_MIN:
        return S16_MIN
    if r > S16_MAX:
        return S16_MAX
    return r


class NopFilter:
    def __init__(self, delay_samples: int):
        self.delay_samples = delay_samples
        self.i = 0

    def has_next_state(self) -> bool:
        return self.i < self.delay_samples

    def next_state(self) -> typing.Dict:
        self.i += 1
        return {}


class DelayedAmplitudeFilter:
    def __init__(self, initial_amplitude: float, target_amplitude: float, delay_samples: int):
        self.initial_amplitude = initial_amplitude
        self.delay_samples = delay_samples
        self.i = 0
        self.d = (target_amplitude - initial_amplitude) / delay_samples

    def has_next_state(self) -> bool:
        return self.i < self.delay_samples

    def next_state(self) -> typing.Dict[str, typing.Dict[str, float]]:
        s = {"state": {"amplitude": self.initial_amplitude + (self.i * self.d)}}
        self.i += 1
        return s


class FilterManager:
    def __init__(self, initial_amplitude: float,
                 filter_definitions: typing.List[typing.Dict],
                 does_repeat: bool):
        self.initial_amplitude = initial_amplitude
        self.filters = list(map(self.make_filter, filter_definitions))
        self.does_repeat = does_repeat
        self.i = 0

    def make_filter(self, filter_definition: typing.Dict) -> typing.Union[NopFilter, DelayedAmplitudeFilter]:
        name = filter_definition["name"]

        if name == "vrms":
            return DelayedAmplitudeFilter(self.initial_amplitude,
                                          filter_definition["target_vrms"] * SQRT_2,
                                          filter_definition["delay_samples"])
        elif name == "nop":
            return NopFilter(filter_definition["delay_samples"])
        else:
            raise RuntimeError("Unknown filter name {}".format(name))

    def current_filter(self) -> typing.Union[NopFilter, DelayedAmplitudeFilter]:
        return self.filters[self.i]

    def next_filter(self) -> typing.Union[NopFilter, DelayedAmplitudeFilter]:
        self.i += 1
        # Not at end of filter list
        if self.i < len(self.filters):
            return self.filters[self.i]
        # At end of filter list
        else:
            # Start again with first filter if filters repeat
            if self.does_repeat:
                self.i = 0
                for f in self.filters:
                    f.i = 0
                return self.filters[self.i]
            # No more filters to return
            else:
                return None

    def next_state(self) -> typing.Dict:
        current_filter = self.current_filter()
        if current_filter.has_next_state():
            return current_filter.next_state()
        else:
            next_filter = self.next_filter()
            if next_filter is not None:
                return next_filter.next_state()
            else:
                return None


class WaveformGenerator:
    def __init__(self):
        self.amplitude: float = 120.0 * SQRT_2
        self.frequency: float = 60.0
        self.phase: float = 0.0
        self.sample_rate_hz: float = 12000.0
        self.samples_per_cycle: int = 200
        self.generator: typing.Generator[typing.Tuple[int, float]] = None
        self.filter_manager: FilterManager = None

    def safe_update(self, state: typing.Dict):
        if len(state) == 0:
            return

        if "state" in state:
            for k, v in state["state"].items():
                if k in self.__dict__ and type(v) is type(self.__dict__[k]):
                    self.__dict__[k] = v
        elif "filters" in state:
            self.filter_manager = FilterManager(self.amplitude, state["filters"], state["does_repeat"])
        else:
            pass

    def waveform_gen(self, start: int = 0):
        i = start
        while True:
            if self.filter_manager is not None:
                next_state = self.filter_manager.next_state()
                if next_state is not None:
                    self.safe_update(next_state)
                else:
                    self.filter_manager = None
            v = self.amplitude * math.sin(self.frequency * (2 * math.pi) * i / self.sample_rate_hz)
            yield (i, v)

            i += 1
            if i == self.samples_per_cycle:
                i = 0

    def next(self) -> typing.Tuple[int, float]:
        return next(self.generator)

    def worker(self, update_queue: multiprocessing.Queue):
        self.generator = self.waveform_gen()
        while True:
            if not update_queue.empty():
                try:
                    self.safe_update(update_queue.get_nowait())
                except queue.Empty as e:
                    pass
            else:
                print(scale_to_sint16(self.next()[1]))
                # print(as_vrms(scale_to_sint16(self.next()[1])))
                time.sleep(1 / self.sample_rate_hz)
                # time.sleep(.1)


def sim_request_handler_factory(queue: multiprocessing.Queue, verbose: bool = False):
    class SimRequestHandler(http.server.BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            self.queue = queue
            super().__init__(request, client_address, server)

        def _set_headers(self, resp: int):
            self.send_response(resp)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        def do_GET(self):
            self._set_headers(200)
            self.wfile.write(json.dumps({"error": "Please POST requests"}).encode())

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data_dict = json.loads(post_data)
            self.queue.put_nowait(data_dict)
            self._set_headers(200)

        def log_message(self, format, *args):
            if verbose:
                super().log_message(format, *args)


    return SimRequestHandler


if __name__ == "__main__":
    parser = argparse.ArgumentParser("sim.py",
                                     "python3 sim.py",
                                     "Box simulator server")
    parser.add_argument("--port", "-p",
                        type=int,
                        default=8000,
                        help="Specified port number to serve from")

    parser.add_argument("--verbose", "-v",
                        help="Verbose output",
                        default=False,
                        action="store_true")

    args = parser.parse_args()

    waveform_gen = WaveformGenerator()
    queue = multiprocessing.Queue()
    httpd = http.server.HTTPServer(("", args.port), sim_request_handler_factory(queue, args.verbose))
    gen_proc = multiprocessing.Process(target=waveform_gen.worker, args=(queue,))

    try:
        if args.verbose:
            print("Starting opq-sim server on port {}...".format(args.port))
        gen_proc.start()
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    if args.verbose:
        print("Stopping opq-sim server... ", end="")
    gen_proc.join()
    httpd.server_close()
    if args.verbose:
        print("Done.")
