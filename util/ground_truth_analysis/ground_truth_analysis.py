import datetime
from typing import *

import matplotlib.pyplot as plt

class DataPoint:
    def __init__(self,
                 ts_s: int,
                 actual_v: float,
                 min_v: float,
                 max_v: float,
                 avg_v: float,
                 stddev_v: float) -> None:
        self.ts_s: int = ts_s
        self.actual_v: float = actual_v
        self.min_v: float = min_v
        self.max_v: float = max_v
        self.avg_v: float = avg_v
        self.stddev_v: float = stddev_v

    @staticmethod
    def from_line(line: str) -> 'DataPoint':
        split_line = line.split(" ")
        ts_s = int(split_line[0])
        actual_v = float(split_line[1])
        min_v = float(split_line[2])
        max_v = float(split_line[3])
        avg_v = float(split_line[4])
        stddev_v = float(split_line[5])

        return DataPoint(ts_s, actual_v, min_v, max_v, avg_v, stddev_v)

    def __str__(self) -> str:
        return f"{self.ts_s} {self.actual_v} {self.min_v} {self.max_v} {self.avg_v} {self.stddev_v}"


def parse_file(path: str) -> List[DataPoint]:
    with open(path, "r") as fin:
        lines: List[str] = list(map(lambda line: line.strip(), fin.readlines()))
        return list(map(DataPoint.from_line, lines))

def plot_path(path: str) -> None:
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    fig: plt.Figure = fig
    ax: plt.Axes = ax

    split_path = path.split("/")
    feature = split_path[-1]
    meter = split_path[-2]

    data_points: List[DataPoint] = parse_file(path)
    dts: List[datetime.datetime] = list(map(lambda data_point: datetime.datetime.utcfromtimestamp(data_point.ts_s), data_points))
    # actuals: List[float] = list(map(lambda data_point: data_point.actual_v, data_points))
    mins: List[float] = list(map(lambda data_point: data_point.min_v, data_points))
    maxes: List[float] = list(map(lambda data_point: data_point.max_v, data_points))
    averages: List[float] = list(map(lambda data_point: data_point.avg_v, data_points))


    # ax.plot(dts, actuals)
    ax.plot(dts, mins, label="Min")
    ax.plot(dts, maxes, label="Max")
    ax.plot(dts, averages, label="Average")

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(f"{feature}")
    ax.set_title(f"{meter} {feature} {dts[0].strftime('%Y-%m-%d')} to {dts[-1].strftime('%Y-%m-%d')}")


    ax.legend()
    fig.show()

def plot_dir(path: str) -> None:
    pass



if __name__ == "__main__":
    # data_points: List[DataPoint] = parse_file("/Users/anthony/scrap/ground_truth_data/POST_MAIN_1/Frequency")
    #
    # for data_point in data_points:
    #     print(data_point)
    plot_path(["/Users/anthony/scrap/ground_truth_data/MARINE_SCIENCE_MAIN_A_MTR/VCN"])
