import json

import sseclient


class OpqBoxMetric:
    def __init__(self, data_dict):
        metrics = data_dict["metrics"]
        for metric in metrics:
            if metric["name"] == "f":
                self.f = metric["value"]
            if metric["name"] == "rms":
                self.rms = metric["value"]
            if metric["name"] == "thd":
                self.thd = metric["value"]

    def __str__(self):
        return json.dumps({"f": self.f,
                           "rms": self.rms,
                           "thd": self.thd})


def get_live_box_data(url,
                      metric_handler = None):
    client = sseclient.SSEClient(url)
    for msg in client:
        metric = OpqBoxMetric(json.loads(msg.data.decode('string-escape').strip('"')))
        if metric_handler is None:
            yield metric
        else:
            yield metric_handler(metric)


def get_live_box_data_single(url,
                             metric_handler = None):
    client = sseclient.SSEClient(url)
    for msg in client:
        metric = OpqBoxMetric(json.loads(msg.data.decode('string-escape').strip('"')))
        if metric_handler is None:
            return metric
        else:
            return metric_handler(metric)


if __name__ == "__main__":

    def metric_handler(opq_box_metric):
        print str(opq_box_metric)

    get_live_box_data_single("http://10.0.1.8:3012/push/0")
