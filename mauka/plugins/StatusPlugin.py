import plugins.base


def run_plugin(config):
    plugins.base.run_plugin(StatusPlugin, config)


class StatusPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
        super().__init__(config, ["heartbeat"], "StatusPlugin")

    def on_message(self, topic, message):
        print("status", topic, message)
