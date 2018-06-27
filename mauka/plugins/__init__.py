"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""

from plugins.acquisition_trigger_plugin import AcquisitionTriggerPlugin
from plugins.frequency_threshold_plugin import FrequencyThresholdPlugin
from plugins.itic_plugin import IticPlugin
from plugins.makai_event_plugin import MakaiEventPlugin
from plugins.status_plugin import StatusPlugin
from plugins.thd_plugin import ThdPlugin
from plugins.voltage_threshold_plugin import VoltageThresholdPlugin
