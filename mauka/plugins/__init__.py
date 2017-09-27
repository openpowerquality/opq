"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""

from plugins.AcquisitionTriggerPlugin import AcquisitionTriggerPlugin
from plugins.FrequencyThresholdPlugin import FrequencyThresholdPlugin
from plugins.MeasurementPlugin import MeasurementPlugin
from plugins.StatusPlugin import StatusPlugin
from plugins.VoltageThresholdPlugin import VoltageThresholdPlugin

from plugins.broker import start_makai_bridge
from plugins.broker import start_mauka_pub_sub_broker
from plugins.manager import PluginManager


