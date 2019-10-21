import datetime
import typing

box_to_location: typing.Dict[str, str] = {
    "1000": "POST 1",
    "1001": "Hamilton",
    "1002": "POST 2",
    "1003": "LAVA Lab",
    "1005": "Parking Structure Ph II",
    "1006": "Frog 1",
    "1007": "Frog 2",
    "1008": "Mile's Office",
    "1009": "Watanabe",
    "1010": "Holmes",
    "1021": "Marine Science Building",
    "1022": "Ag. Engineering",
    "1023": "Law Library",
    "1024": "IT Building",
    "1025": "Kennedy Theater"
}

incident_map: typing.Dict[str, str] = {
    "FREQUENCY_SWELL": "F Swell",
    "FREQUENCY_SAG": "F Sag",
    "FREQUENCY_INTERRUPTION": "F Int",
    "OUTAGE": "Outage"
}


def any_of_in(a: typing.List, b: typing.List) -> bool:
    a = set(a)
    b = set(b)
    return len(a.intersection(b)) > 0


def fmt_ts_by_hour(ts_s: int) -> str:
    dt = datetime.datetime.utcfromtimestamp(ts_s)
    return dt.strftime("%Y-%m-%d")
