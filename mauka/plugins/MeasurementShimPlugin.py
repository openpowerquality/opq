import plugins.base


def run_plugin(config):
    plugins.base.run_plugin(MeasurementShimPlugin, config)


def is_measurement_topic(topic):
    if isinstance(topic, int):
        return True
    elif isinstance(topic, str):
        return topic.isdigit()
    else:
        return False


class MeasurementShimPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
        super().__init__(config, [""], "MeasurementShimPlugin")

    def on_message(self, topic, message):
        if is_measurement_topic(topic):
            new_topic = "measurement".format(topic)
            self.produce(new_topic.encode(), message)
