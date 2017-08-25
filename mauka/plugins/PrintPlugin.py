import plugins.base


def run_plugin(config):
    plugins.base.run_plugin(PrintPlugin, config)


class PrintPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
        super().__init__(config, [""], "PrintPlugin")

    def on_message(self, topic, message):
        print("topic: {} message: {}...".format(topic, str(message)[:30]))
