import datetime
from typing import *

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


def bin_dt_by_min(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0, 0, tzinfo=datetime.timezone.utc)


def align_data_by_min(series_a: List[A],
                      series_b: List[B],
                      dt_func_a: Callable[[A], datetime.datetime],
                      dt_func_b: Callable[[B], datetime.datetime],
                      v_func_a: Callable[[A], C],
                      v_func_b: Callable[[B], D]) -> Tuple[List[datetime.datetime],
                                                           List[C],
                                                           List[datetime.datetime],
                                                           List[D]]:
    dts_a = list(map(dt_func_a, series_a))
    dts_b: List[datetime.datetime] = list(map(dt_func_b, series_b))

    binned_dts_a: List[datetime.datetime] = list(map(bin_dt_by_min, dts_a))
    binned_dts_b: List[datetime.datetime] = list(map(bin_dt_by_min, dts_b))

    intersecting_dts: Set[datetime.datetime] = set(binned_dts_a).intersection(set(binned_dts_b))

    aligned_a_dts: List[datetime.datetime] = []
    aligned_a_vs: List[C] = []
    aligned_b_dts: List[datetime.datetime] = []
    aligned_b_vs: List[D] = []

    already_seen_a: Set[datetime.datetime] = set()
    already_seen_b: Set[datetime.datetime] = set()

    for i, dt in enumerate(binned_dts_a):
        if dt in intersecting_dts and dt not in already_seen_a:
            aligned_a_dts.append(dt)
            aligned_a_vs.append(v_func_a(series_a[i]))
            already_seen_a.add(dt)

    for i, dt in enumerate(binned_dts_b):
        if dt in intersecting_dts and dt not in already_seen_b:
            aligned_b_dts.append(dt)
            aligned_b_vs.append(v_func_b(series_b[i]))
            already_seen_b.add(dt)

    return aligned_a_dts, aligned_a_vs, aligned_b_dts, aligned_b_vs
