#!/usr/local/bin/python3.6

import argparse
import http.client
import http.server
import json
import math
import multiprocessing
import os
import struct
import sys
import time
import typing
import queue

SAMPLES_PER_CYCLE: int = 200
"""Number of samples per waveform cycle"""

DEVICE_HANDLE: str = "/tmp/opqsim"
"""Device handle"""

SQRT_2: float = math.sqrt(2)
"""Constant for the sqrt(2)"""


S16_MIN: int = -(2 ** 15)
"""Minimum value for signed 16-bit integer"""


S16_MAX: int = 2 ** 15 - 1
"""Maximum value for signed 16-bit integer"""


class OpqDeviceFifo:
    def __init__(self):
        if not os.path.exists(DEVICE_HANDLE):
            os.mkfifo(DEVICE_HANDLE)
        self.fd = open(DEVICE_HANDLE, 'wb')
        self.samples = []
        self.last_gps_counter = 0
        self.current_counter = 0
        self.flags = 0
        self.sleep = 1.0 / 60.0

    def add_sample(self, sample):
        if len(self.samples) >= SAMPLES_PER_CYCLE:
            self.dump()
        self.samples.append(sample)

    def dump(self):
        ret = b""
        for s in self.samples:
            ret += struct.pack('h', s)
        ret += struct.pack('H', self.last_gps_counter)
        ret += struct.pack('H', self.current_counter)

        ret += struct.pack('I', self.flags)
        self.samples = []
        try:
            self.fd.write(ret)
            time.sleep(self.sleep)
        except:
            self.fd = open(DEVICE_HANDLE, 'wb')


def as_vrms(v: int, calibration_constant: float = 152.0) -> float:
    """
    Converts a signed 16-bit simulated DAC reading into Vrms.
    :param v: The 16-bit signed integer simulated DAC reading.
    :param calibration_constant: Calibration constant for device we are converted for.
    :return: Vrms
    """
    return (v / calibration_constant) / SQRT_2


def scale_to_sint16(v: float, calibration_constant: float = 152.0) -> int:
    """
    Converts a raw voltage reading to a signed 16-bit integer.
    :param v: Raw voltage.
    :param calibration_constant: Device calibration constant.
    :return: Scaled and signed 16-bit integer.
    """
    r = round(v * calibration_constant)
    if r < S16_MIN:
        return S16_MIN
    if r > S16_MAX:
        return S16_MAX
    return r


class DelayedStateFilter:
    """
    This class represents a base class for filters who change the state of waveform generation using a delay where the
    delay is specified in number of samples.
    """
    def __init__(self,
                 initial_value: float,
                 target_value: float,
                 delay_samples: int,
                 state_arg: str):
        """
        Initializes this delayed state filter
        :param initial_value: The initial value of the filter
        :param target_value: The target value of the filter
        :param delay_samples: The number of samples to get from initial_value to target_value.
        :param state_arg: The state field that is being modified.
        """

        self.initial_value: float = initial_value
        """The starting state value"""

        self.delay_samples: int = delay_samples
        """The total number of samples to delay before hitting target value"""

        self.i: int = 0
        """Index into the filter state"""

        self.d: float = (target_value - initial_value) / delay_samples
        """Delta that selected state arg changes for each sample"""

        self.state_arg: str = state_arg
        """Name of the value in the waveform state that will be changing (e.g. amplitude, frequency, etc..."""

    def has_next_state(self) -> bool:
        """
        :return: If this filter has a next state or not.
        """
        return self.i < self.delay_samples

    def next_state(self) -> typing.Dict[str, typing.Dict[str, float]]:
        """
        :return: The next state of this filter
        """
        s = {"state": {self.state_arg: self.initial_value + (self.i * self.d)}}
        self.i += 1
        return s


class NopFilter(DelayedStateFilter):
    """
    The nop filter does nothing for the specified number of samples.
    The state of the waveform generator will remain as it was since the last state change.
    """
    def __init__(self, delay_samples: int):
        """
        :param delay_samples: Number of samples for this filter to do nothing for.
        """
        super().__init__(0, 0, delay_samples, "")

    def next_state(self) -> typing.Dict:
        """
        :return: An empty state.
        """
        super().next_state()
        return {}


class DelayedAmplitudeFilter(DelayedStateFilter):
    """
    This filter changes the amplitude from it's current amplitude to a new amplitude over a given number of cycles.
    """
    def __init__(self, initial_amplitude: float, target_amplitude: float, delay_samples: int):
        """
        :param initial_amplitude: Initial waveform amplitude (raw voltage not RMS)
        :param target_amplitude: Target waveform amplitude
        :param delay_samples: Number of samples it takes to go from initial to target
        """
        super().__init__(initial_amplitude, target_amplitude, delay_samples, "amplitude")


class DelayedFrequencyFilter(DelayedStateFilter):
    """
    This filter changes the frequency from it's current frequency to a new frequency over a given number of cycles.
    """
    def __init__(self, initial_frequency: float, target_frequency: float, delay_samples: int):
        super().__init__(initial_frequency, target_frequency, delay_samples, "frequency")


class FilterManager:
    """
    This class manages the state of the current list of filters.
    """
    def __init__(self,
                 initial_amplitude: float,
                 initial_frequency: float,
                 filter_definitions: typing.List[typing.Dict],
                 does_repeat: bool):
        """
        :param initial_amplitude: Amplitude when this filter was created
        :param initial_frequency: Frequency when this filter was created
        :param filter_definitions: Filters currently being managed
        :param does_repeat: Does the list of filters repeat after finishing with the last filter?
        """

        self.initial_amplitude: float = initial_amplitude
        """Amplitude when this filter was created"""

        self.initial_frequency: float = initial_frequency
        """Frequency when this filter was created"""

        self.filters = list(map(self.make_filter, filter_definitions))
        """Filters currently being manage"""

        self.does_repeat: bool = does_repeat
        """Does the list of filters repeat after finishing with the last filter?"""

        self.i: int = 0
        """Index into the list of filters"""

    def make_filter(self, filter_definition: typing.Dict) -> typing.Union[NopFilter,
                                                                          DelayedAmplitudeFilter,
                                                                          DelayedFrequencyFilter]:
        """
        Given a filter definition, parse the required fields and create an instance of the request filter.
        :param filter_definition: Definition provides as JSON string.
        :return: Filter instance from definition.
        """
        name = filter_definition["name"]

        if name == "vrms":
            return DelayedAmplitudeFilter(self.initial_amplitude,
                                          filter_definition["target_vrms"] * SQRT_2,
                                          filter_definition["delay_samples"])
        elif name == "frequency":
            return DelayedFrequencyFilter(self.initial_frequency,
                                          filter_definition["target_frequency"],
                                          filter_definition["delay_samples"])
        elif name == "nop":
            return NopFilter(filter_definition["delay_samples"])
        else:
            raise RuntimeError("Unknown filter name {}".format(name))

    def current_filter(self) -> typing.Union[NopFilter,
                                             DelayedAmplitudeFilter,
                                             DelayedFrequencyFilter]:
        """
        :return: The current filter.
        """
        return self.filters[self.i]

    def next_filter(self) -> typing.Union[NopFilter,
                                          DelayedAmplitudeFilter,
                                          DelayedFrequencyFilter]:
        """Returns the next filter or None if there are no more filters"""

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
        """Returns the next state from the currently filter."""
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
    """
    This class generates a simulated waveform where the amplitude, frequency, phase, and sample rate can be altered
    to change the state of the waveform generator.
    """
    def __init__(self, debug: bool = False):
        self.amplitude: float = 120.0 * SQRT_2
        """Amplitude of the waveform"""

        self.frequency: float = 60.0
        """Frequency of the waveform"""

        self.phase: float = 0.0
        """Phase of the waveform"""

        self.sample_rate_hz: float = 12000.0
        """Sampling rate of the waveform"""

        self.samples_per_cycle: int = 200
        """Number of samples per cycle in the waveform"""

        self.generator: typing.Generator[typing.Tuple[int, float]] = None
        """A Python generator that lazily produces the waveform"""

        self.filter_manager: FilterManager = None
        """Allows us to apply filters to the waveform"""

        self.debug: bool = debug
        """Should we print information to stdout in debug format?"""

    def safe_update(self, state: typing.Dict):
        """
        Udates the state of the waveform generator.
        :param state:
        :return:
        """
        if len(state) == 0:
            return

        if "reset" in state and state["reset"]:
            self.filter_manager = None

        if "state" in state:
            for k, v in state["state"].items():
                if k in self.__dict__ and type(v) is type(self.__dict__[k]):
                    self.__dict__[k] = v
        elif "filters" in state:
            self.filter_manager = FilterManager(self.amplitude,
                                                self.frequency,
                                                state["filters"],
                                                state["does_repeat"])
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
            v = self.amplitude * math.sin(self.frequency * (2 * math.pi) * (i / self.sample_rate_hz))
            yield (i, v)

            i += 1
            if i == self.samples_per_cycle:
                i = 0

    def next(self) -> typing.Tuple[int, float]:
        return next(self.generator)

    def worker(self, update_queue: multiprocessing.Queue):
        self.generator = self.waveform_gen()
        if not self.debug:
            fifo = OpqDeviceFifo()
        while True:
            if not update_queue.empty():
                try:
                    self.safe_update(update_queue.get_nowait())
                except queue.Empty as e:
                    pass
            else:
                if self.debug:
                    print(as_vrms(scale_to_sint16(self.next()[1])))
                    time.sleep(.1)
                else:
                    fifo.add_sample(scale_to_sint16(self.next()[1]))
                    # time.sleep(1 / self.sample_rate_hz)


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


def update_state_post_request(config_path: str, port: int, verbose: bool):
    with open(config_path, "r") as json_in:
        c = json.load(json_in)
        connection = http.client.HTTPConnection("localhost", port)
        connection.request("POST", "/", json.dumps(c), {'Content-type': 'application/json'})
        response = connection.getresponse()
        if verbose:
            print(response.read().decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser("sim.py",
                                     "python3 sim.py",
                                     "Box simulator server")

    parser.add_argument("--port", "-p",
                        type=int,
                        default=8000,
                        help="Specified port number to serve from")

    parser.add_argument("--state", "-s",
                        help="Location of json config file")

    parser.add_argument("--verbose", "-v",
                        help="Verbose output",
                        default=False,
                        action="store_true")

    parser.add_argument("--debug", "-d",
                        help="Display values as rms voltage and slow down the sample rate to .1 seconds",
                        default=False,
                        action="store_true")

    args = parser.parse_args()
    if "state" in args and args.state is not None:
        update_state_post_request(args.state, args.port, args.verbose)
        sys.exit(0)

    waveform_gen = WaveformGenerator(args.debug)
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
