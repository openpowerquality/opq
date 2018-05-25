import json
import typing


def sec2samples(s: float) -> int:
    return int(s * 60 * 200)


def cycles2samples(c: float) -> int:
    return int(c * 200)


def make_nop_filter(delay_samples: int) -> typing.Dict:
    return {
        "name": "nop",
        "delay_samples": delay_samples
    }


def make_vrms_filter(target_vrms: float, delay_samples: int) -> typing.Dict:
    return {
        "name": "vrms",
        "target_vrms": target_vrms,
        "delay_samples": delay_samples
    }


def make_candidate_waveform(padding: int, duration: int, pu: float):
    t = "sag" if pu < 1 else "swell"
    fn = "configs/ieee1159/{}_{}_{}_{}.json".format(t, padding, duration, pu)
    delay_len = 400

    c = {
        "filters": [
            make_nop_filter(padding),
            make_vrms_filter(120 * pu, delay_len),
            make_nop_filter(duration - (2 * delay_len)),
            make_vrms_filter(120.0, delay_len),
            make_nop_filter(padding)
        ],
        "does_repeat": False
    }

    with open(fn, "w") as fout:
        json.dump(c, fout, indent=2)


# Instantaneous sags
make_candidate_waveform(sec2samples(.1), cycles2samples(25), .9)
make_candidate_waveform(sec2samples(.1), cycles2samples(25), .5)
make_candidate_waveform(sec2samples(.1), cycles2samples(25), .1)

# Instantaneous swells
make_candidate_waveform(sec2samples(.1), cycles2samples(25), 1.1)
make_candidate_waveform(sec2samples(.1), cycles2samples(25), 1.4)
make_candidate_waveform(sec2samples(.1), cycles2samples(25), 1.8)

# Momentary interruptions
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), .09)
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), .01)

# Momentary sags
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), .9)
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), .5)
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), .1)

# Momentary swells
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), 1.1)
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), 1.4)
make_candidate_waveform(sec2samples(.1), sec2samples(2.5), 1.8)

# Temporary interruptions
make_candidate_waveform(sec2samples(.1), sec2samples(5), .09)
make_candidate_waveform(sec2samples(.1), sec2samples(5), .01)

# Temporary sags
make_candidate_waveform(sec2samples(.1), sec2samples(5), .9)
make_candidate_waveform(sec2samples(.1), sec2samples(5), .5)
make_candidate_waveform(sec2samples(.1), sec2samples(5), .1)

# Temporary swells
make_candidate_waveform(sec2samples(.1), sec2samples(5), 1.1)
make_candidate_waveform(sec2samples(.1), sec2samples(5), 1.4)
make_candidate_waveform(sec2samples(.1), sec2samples(5), 1.8)

import glob
import subprocess

configs = glob.glob("configs/ieee1159/*.json")
for config in configs:
    fn = config.split("/")[2][:-5]
    fn_s = fn.split("_")
    total_samples = str(2 * int(fn_s[1]) + int(fn_s[2]))
    txt_out = "configs/ieee1159/" + fn + ".txt"
    f = open(txt_out, "w")
    subprocess.run(["python3", "sim-gen.py", config, total_samples], stdout=f)
    f.close()

    png_out = "configs/ieee1159/{}.png".format(fn)
    subprocess.run(["gnuplot", "-e", "set terminal png; set output '{}'; plot '{}'".format(png_out, txt_out)])

    subprocess.run(["python3", "import_waveform.py", txt_out, fn])
