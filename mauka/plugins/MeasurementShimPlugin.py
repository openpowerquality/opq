"""
This modules contains the measurement shim plugin who reads raw triggering messages and converts them into
measurement measurements that this system can use
"""

import typing

import plugins.base


def run_plugin(config: typing.Dict):
    """Runs this plugin using the given configuration

    :param config: Configuration dictionary
    """
    plugins.base.run_plugin(MeasurementShimPlugin, config)


def is_measurement_topic(topic) -> bool:
    """Determines if the given topic is a measurement topic or not

    Since this plugin reads all topics, we need to determine if raw triggering message is a topic or not

    :param topic: Topic to be tested
    :return: If this is a measurement topic or not
    """
    if isinstance(topic, int):
        return True
    elif isinstance(topic, str):
        return topic.isdigit()
    else:
        return False


class MeasurementShimPlugin(plugins.base.MaukaPlugin):
    """
    This class contains the measurement shim plugin who reads raw triggering messages and converts them into
    measurement measurements that this system can use
    """
    def __init__(self, config: typing.Dict):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, [""], "MeasurementShimPlugin")

    def on_message(self, topic, message):
        """Subscribed messages occur async

        Messages are forwarded as measurements to measurement plugin

        :param topic: The topic that this message is associated with
        :param message: The message
        """
        if is_measurement_topic(topic):
            new_topic = "measurement".format(topic)
            self.produce(new_topic.encode(), message)
