import argparse
import datetime
import typing

import matplotlib.dates as md
import matplotlib.pyplot as plt


def local_dt_to_ts_s(local_dt: datetime.datetime) -> float:
    return local_dt.timestamp()


def get_trends(start_ts_ms_utc: int, end_ts_ms_utc: int) -> typing.Dict[str, typing.List[typing.Dict]]:
    pass


def analyze_solar_data(solar_data_csv_path: str):
    with open(solar_data_csv_path, "r") as fin:
        lines = list(map(lambda line: line.strip().replace('"', ""), fin.readlines()[1:]))
        timestamps = []
        elkor_prod_meter_kw = []
        inverters_kw = []

        for line in lines:
            split_line = line.split(",")
            timestamps.append(split_line[0])
            elkor_value = float(split_line[1]) if len(split_line[1]) > 0 else None
            elkor_prod_meter_kw.append(elkor_value)
            inverter_value = float(split_line[2]) if len(split_line[2]) > 0 else None
            inverters_kw.append(inverter_value)

        dts = list(map(lambda ts: datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"), timestamps))

        start_ts_s_utc = local_dt_to_ts_s(dts[0])
        end_ts_s_utc = local_dt_to_ts_s(dts[-1])

        fig, axes = plt.subplots(2, 1, figsize=(16, 9))
        fig: plt.Figure = fig
        axes: typing.List[plt.Axes] = axes

        # Solar ax
        ax_solar = axes[0]
        ax_solar.plot(dts, inverters_kw, label="Inverters Kilowatts")
        ax_solar.plot(dts, elkor_prod_meter_kw, label="Elkor Production Meter Kilowatts")

        ax_solar.set_xlabel("Site Time")
        ax_solar.set_ylabel("Kilowatts")
        fmt = md.DateFormatter("%d %H:%M")
        ax_solar.xaxis.set_major_formatter(fmt)

        ax_solar.legend()
        plt.show()


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("solar_data_csv_path")
    ARGS = PARSER.parse_args()
    analyze_solar_data(ARGS.solar_data_csv_path)
