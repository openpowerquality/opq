"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""

from plugins.AcquisitionTriggerPlugin import AcquisitionTriggerPlugin
from plugins.FrequencyThresholdPlugin import FrequencyThresholdPlugin
from plugins.IticPlugin import IticPlugin
from plugins.MeasurementPlugin import MeasurementPlugin
from plugins.StatusPlugin import StatusPlugin
from plugins.ThdPlugin import ThdPlugin
from plugins.VoltageThresholdPlugin import VoltageThresholdPlugin


