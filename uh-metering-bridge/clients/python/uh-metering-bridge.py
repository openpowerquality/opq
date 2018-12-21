import json
import typing
import urllib.request


def make_req(end_point: str, as_json: bool = True):
    with urllib.request.urlopen("http://localhost:13000%s" % end_point) as response:
        data = response.read()
        if as_json:
            return json.loads(data)

        return data


def health_check() -> bytes:
    return make_req("/", as_json=False)


def all_available_meters() -> typing.List[str]:
    return make_req("/meters")


def all_available_features() -> typing.List[str]:
    return make_req("/features")


def available_meters(feature) -> typing.List[str]:
    return make_req("/meters/%s" % feature)


def available_features(meter) -> typing.List[str]:
    return make_req("/features/%s" % meter)


def meters_to_features() -> typing.Dict[str, typing.List[str]]:
    return make_req("/meters_to_features")


def features_to_meters() -> typing.Dict[str, typing.List[str]]:
    return make_req("/features_to_meters")


def scrape_data(meter: str, feature: str, start_ts: int, end_ts: int):
    return make_req("/data/%s/%s/%d/%d" % (meter, feature, start_ts, end_ts))


if __name__ == "__main__":
    print(scrape_data("AG_ENGINEERING_MAIN_MTR", "Frequency", 1545220518, 1545224118))
