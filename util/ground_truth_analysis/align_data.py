import datetime
from typing import *

A = TypeVar("A")
B = TypeVar("B")


def align_data_by_minute(series_a: List[A],
                         series_b: List[B],
                         dt_func_a: Callable[[A], datetime.datetime],
                         dt_func_b: Callable[[B], datetime.datetime]) -> Tuple[List[A], List[B]]:
    dts_a: List[datetime.datetime] = list(map(dt_func_a, series_a))
    dts_b: List[datetime.datetime] = list(map(dt_func_b, series_b))

    binned_dts_a: List[datetime.datetime] = list(map(lambda dt: datetime.datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute
    ), dts_a))

    binned_dts_b: List[datetime.datetime] = list(map(lambda dt: datetime.datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute
    ), dts_b))

    intersecting_dts: Set[datetime.datetime] = set(binned_dts_a).intersection(set(binned_dts_b))

    aligned_a: List[A] = []
    aligned_b: List[B] = []

    for i, dt in binned_dts_a:
        if dt in intersecting_dts:
            aligned_a.append(series_a[i])

    for i, dt in binned_dts_b:
        if dt in intersecting_dts:
            aligned_b.append(series_b[i])

    return aligned_a, aligned_b
