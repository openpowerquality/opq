import datetime

MS_IN_S = 1000.0


def ms_to_s(ms: float) -> float:
    return ms / MS_IN_S


def datetime_from_epoch_ms(epoch_ms_utc: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(ms_to_s(epoch_ms_utc))
