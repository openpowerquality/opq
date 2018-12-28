import json
import time
import typing
import urllib.request


def make_req(end_point: str, as_json: bool = True) -> typing.Union[bytes,
                                                                   typing.List,
                                                                   typing.Dict]:
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


def scrape_data(meter: str, feature: str, start_ts: int, end_ts: int) -> typing.List[typing.Dict]:
    return make_req("/data/%s/%s/%d/%d" % (meter, feature, start_ts, end_ts))


def download_data_with_features(features: typing.List[str], start_ts: int, end_ts: int, sleep: float = 2.0) -> typing.List[typing.List[typing.Dict]]:
    empty = 0
    non_empty = 0
    data = []
    for feature in features:
        meters = available_meters(feature)
        for meter in meters:
            meter_feature_data = scrape_data(meter, feature, start_ts, end_ts)
            if meter_feature_data is not None and len(meter_feature_data) > 0:
                print("+ GET %s %s %d %d" % (meter, feature, start_ts, end_ts))
                data.append(meter_feature_data)
                non_empty += 1
            else:
                print("- GET %s %s %d %d" % (meter, feature, start_ts, end_ts))
                empty += 1
            time.sleep(sleep)
        time.sleep(5)
        print("Empty %d non-empty %d" % (empty, non_empty))
    return data


def download_data_with_features_past(features: typing.List[str], past_seconds: int) -> typing.List[
    typing.List[typing.Dict]]:
    now_ts = int(round(time.time()))
    past = now_ts - past_seconds
    return download_data_with_features(features, past, now_ts)


def download_data_with_features_past_day(features: typing.List[str]) -> typing.List[typing.List[typing.Dict]]:
    return download_data_with_features_past(features, 86400)


def download_data_with_features_past_hour(features: typing.List[str]) -> typing.List[typing.List[typing.Dict]]:
    return download_data_with_features_past(features, 3600)




if __name__ == "__main__":
    with open("data.json", "w") as fout:
        data = download_data_with_features_past(["Frequency"], 60 * 15)
        print(data)
        json.dump(data, fout)
