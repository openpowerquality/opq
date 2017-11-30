# OPQMauka Plugins

## Base Plugin {#base}

The [base plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/base.py) is a base class which implements common functionally across all plugins. This plugin in subclassed by all other OPQMauka plugins. The functionality this plugin provides includes:

* Access to the underlying Mongo database
* Automatic publish subscribe semantics with ```on_message``` and ```publish``` APIs (via ZMQ)
* Configuration/JSON parsing and loading
* Python multiprocessing primitives 
* Status/heartbeat notifications

## Measurement Plugin {#measurement}

The [measurement plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/MeasurementPlugin.py) records raw triggering data and aggregates it into a measurements collection in our Mongo database. 

These measurements are mainly used for analyzing long term trends and for display in OPQView. It's possible to control the sampling of raw triggering messages by setting the ```plugins.MeasurementPlugin.sample_every``` key in the configuration file.

## Threshold Plugin

The [threshold plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/ThresholdPlugin.py) is a base plugin that implements functionality for determining preset threshold crossings over time. That is, this plugin, given a steady state, will detect deviations from the steady using percent deviation from the steady state as a discriminating factor. 

When subclassing this plugin, other plugins will define the steady state value, the low threshold value, the high threshold value, and the duration threshold value.

This plugin is subclassed by the voltage and frequency threshold plugins.

Internally, the threshold plugin looks at individual measurements and determines if the value is low, stable, or high (as defined by the subclass). A finite state machine is used to switch between the following states and define events.

**Low to low.** Still in a low threshold event. Continue recording low threshold event.

**Low to stable.** Low threshold event just ended. Produce an event message.

**Low to high.** Low threshold event just ended. Produce and event message. Start recording high threshold event.

**Stable to low.** Start recording low threshold event.

** Stable to stable.** Steady state. Nothing to record.

**Stable to high.** Start recording high threshold event.

**High to low.** High threshold event just ended. Produce event message. Start recording low threshold event.

**High to stable.** High threshold event just ended. Produce event message.

**High to high.** Still in high threshold event. Continue recording event. 

Event messages are produced by passing the contents of a recorded event to the ```on_event``` method call. This method call needs to be implemented in all subclassing plugins in order to deal with the recorded event.

## Frequency Threshold Plugin {#frequency}

The [frequency threshold plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/FrequencyThresholdPlugin.py) subclasses the threshold plugin and classifies frequency dips and swells.

By default, this plugin assumes a steady state of 60Hz and will detect dips and swells over 0.5% in either direction. The thresholds can be configured by setting the keys ```plugins.ThresholdPlugin.frequency.ref```, ```plugins.ThresholdPlugin.frequency.threshold.percent.low```, and ```plugins.ThresholdPlugin.frequency.threshold.percent.high``` in the configuration file.

When thresholds are tripped, frequency events are generated and published to the system. These are most importantly used to generate event triggering requests to OPQMauka to request raw data from affected devices.

## Voltage Threshold Plugin {#voltage}

The [voltage threshold plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/VoltageThresholdPlugin.py) subclasses the threshold plugin and classifies voltage dips and swells.

By default, this plugin assumes a steady state of 120hz and will detect dips and swells over 5% in either direction. The thresholds can be configured by setting the keys plugins.ThresholdPlugin.voltage.ref, plugins.ThresholdPlugin.voltage.threshold.percent.low, and plugins.ThresholdPlugin.voltage.threshold.percent.high in the configuration file.

When thresholds are tripped, voltage events are generated and published to the system. These are most importantly used to generate event triggering requests to OPQMauka to request raw data from affected devices.

## Total Harmonic Distortion Plugin {#thd}
The [total harmonic distortion (THD) plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/ThdPlugin.py) subscribes to all events that request data, waits until the data is realized, performs THD calculations over the data, and then stores the results back to the database.

This plugin subscribes to events that request data and also THD specific messages so that this plugin can be triggered to run over historic data as well. The amount of time from when this plugin receives a message until it assumes the data is in the database can be configured in the configuration file. 

The THD calculations are computed in a separate thread and the results are stored back to the database. 

## ITIC Plugin {#itic}
The [ITIC plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/IticPlugin.py) subscribes to all events that request data, waits until the data is realized, performs ITIC calculations over the data, and then stores the results back to the database.

This plugin subscribes to events that request data and also ITIC specific messages so that this plugin can be triggered to run over historic data as well. The amount of time from when this plugin receives a message until it assumes the data is in the database can be configured in the configuration file. 

The ITIC calculations are computed in a separate thread and the results are stored back to the database. 

ITIC regions are determined by plotting the curve and performing a point in polygon algorithm to determine which curve the point falls within.


## Acquisition Trigger Plugin {#acquisition}

The [acquistion trigger plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/AcquisitionTriggerPlugin.py) subscribes to all events and forms event request messages to send to OPQMakai to enable the retrieval of raw power data for higher level analytics.

This plugin employs a deadzone between event messages to ensure that multiple requests for the same data are not sent in large bursts, overwhelming OPQBoxes or OPQMakai. The deadzone by default is set to 60 seconds, but can be configured by setting the ```plugins.AcquisitionTriggerPlugin.sDeadZoneAfterTrigger``` key in the configuration. If this plugin encounters an event while in a deadzone, a request is still generated and sent to OPQMakai, however a flag is set indicating to Makai that raw data should not be requested.


## Status Plugin {#status}

The [status plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/StatusPlugin.py) subscribes to heatbeat messages and logs heartbeats from all other plugins (including itself).

## Print Plugin {#print}

The [print plugin](https://github.com/openpowerquality/opq/blob/master/mauka/plugins/PrintPlugin.py) subscribes to all topics and prints every message. This plugin is generally disabled and mainly only useful for debuggin purposes.

## Plugin Development {#development}

The following steps are required to create a new OPQMauka plugin:

1. Create a new Python module for the plugin in the plugins package (i.e. MyFancyPlugin.py).

2. import the plugin base
```
import plugins.base
```

3. Create a class that extends the base plugin.
```
class MyFancyPlugin(plugins.base.MaukaPlugin):
      ...
```

4. Create the following module level function
```
def run_plugin(config):
      plugins.base.run_plugin(MyFancyPlugin, config)
```

5. Provide the following constructor for your class. Ensure the a call to super provides the configuration, list of topics to subscribe to, and the name of the plugin.
```
def __init__(self, config):
      super().__init__(config, ["foo", "bar"], "MyFancyPlugin")
```

6. Overload the ```on_message``` from the base class. This is how you will receive all the messages from topics you subscribe to.
```
def on_message(self, topic, message):
      ...
```

7. Produce messages by invoking the superclasses produce method.
```
self.produce("topic", "message")
```

8. Import and add your plugin in plugins/```__init__.py```.
```
from plugins import MyFancyPlugin
```

9. Add your plugin to the plugin list in ```OpqMauka.py```.

An example plugin template might look something like:

```
# plugins/MyFancyPlugin.py
import plugins.base

def run_plugin(config):
    plugins.base.run_plugin(MyFancyPlugin, config)

def MyFancyPlugin(plugins.base.MaukaPlugin):
    def __init__(self, config):
         super().__init__(config, ["foo", "bar"], "MyFancyPlugin")

    def on_message(self, topic, message):
          print(topic, message)
```
