"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""
from plugins import AcquisitionTriggerPlugin
from plugins import FrequencyThresholdPlugin
from plugins import MeasurementPlugin
from plugins import MeasurementShimPlugin
from plugins import PrintPlugin
from plugins import StatusPlugin
from plugins import VoltageThresholdPlugin




