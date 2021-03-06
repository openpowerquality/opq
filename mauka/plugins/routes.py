"""
This module provides "type-safe" routes for passing messages around ZMQ.
"""


class Routes:
    """
    This class provides "type-safe" routes for passing messages around ZMQ.
    """
    box_measurement_rate_request = "BoxMeasurementRateRequest"
    box_measurement_rate_response = "BoxMeasurementRateResponse"
    heartbeat = "heartbeat"
    gc_stat = "gc_stat"
    box_optimization_request = "BoxOptimizationRequest"
    windowed_frequency = "windowed_frequency"
    laha_gc = "laha_gc"
    rms_windowed_voltage = "RmsWindowedVoltage"
    adc_samples = "AdcSamples"
    raw_voltage = "RawVoltage"
    makai_event = "MakaiEvent"
    thd_request_event = "ThdRequestEvent"
    threshold_optimization_request = "ThresholdOptimizationRequest"
    trigger_request = "TriggerRequest"
