import math
import typing

import numpy

SAMPLES_PER_CYCLE = 200
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
    def __init__(self, delay_samples: int, waveform_generator):
        self.waveform_generator = waveform_generator
        self.delay_samples = delay_samples
        self.i = 0

    def has_next_state(self) -> bool:
        return self.i < self.delay_samples

    def next_state(self) -> typing.Dict:
        self.i += 1
        return {}


class DelayedAmplitudeFilter:
    def __init__(self, initial_amplitude: float, target_amplitude: float, delay_samples: int, waveform_generator):
        self.initial_amplitude = initial_amplitude
        self.target_amplitude = target_amplitude
        self.delay_samples = delay_samples
        self.i = 0
        self.d = (target_amplitude - initial_amplitude) / delay_samples
        self.waveform_generator = waveform_generator

    def seen_initial_amplitude_from_current_state(self):
        self.initial_amplitude = self.waveform_generator.amplitude
        self.d = (self.target_amplitude - self.initial_amplitude) / self.delay_samples

    def has_next_state(self) -> bool:
        return self.i < self.delay_samples

    def next_state(self) -> typing.Dict[str, typing.Dict[str, float]]:
        if self.i == 0:
            self.seen_initial_amplitude_from_current_state()
        s = {"state": {"amplitude": self.initial_amplitude + (self.i * self.d)}}
        self.i += 1
        return s


class FilterManager:
    def __init__(self, initial_amplitude: float,
                 filter_definitions: typing.List[typing.Dict],
                 does_repeat: bool,
                 waveform_generator):
        self.waveform_generator = waveform_generator
        self.initial_amplitude = initial_amplitude
        self.filters = list(map(self.make_filter, filter_definitions))
        self.does_repeat = does_repeat
        self.i = 0

    def make_filter(self, filter_definition: typing.Dict) -> typing.Union[NopFilter, DelayedAmplitudeFilter]:
        name = filter_definition["name"]

        if name == "vrms":
            return DelayedAmplitudeFilter(self.initial_amplitude,
                                          filter_definition["target_vrms"] * SQRT_2,
                                          filter_definition["delay_samples"], self.waveform_generator)
        elif name == "nop":
            return NopFilter(filter_definition["delay_samples"], self.waveform_generator)
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
    def __init__(self, debug: bool = False):
        self.amplitude: float = 120.0 * SQRT_2
        self.frequency: float = 60.0
        self.phase: float = 0.0
        self.sample_rate_hz: float = 12000.0
        self.samples_per_cycle: int = 200
        self.generator: typing.Generator[typing.Tuple[int, float]] = self.waveform_gen()
        self.filter_manager: FilterManager = None
        self.debug: bool = debug

    def safe_update(self, state: typing.Dict):
        if len(state) == 0:
            return

        if "reset" in state and state["reset"]:
            self.filter_manager = None

        if "state" in state:
            for k, v in state["state"].items():
                if k in self.__dict__ and type(v) is type(self.__dict__[k]):
                    self.__dict__[k] = v
        elif "filters" in state:
            self.filter_manager = FilterManager(self.amplitude, state["filters"], state["does_repeat"], self)
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



if __name__ == "__main__":
    import sys
    import json
    state_file = sys.argv[1]
    total_samples = int(sys.argv[2])
    with open(state_file, "r") as f:
        state = json.load(f)
        gen = WaveformGenerator()
        gen.safe_update(state)
        for i in range(total_samples):
            # print(scale_to_sint16(gen.next()[1]))
            print(scale_to_sint16(gen.next()[1]))


