"""
This module provides "type-safe" routes for passing messages around ZMQ.
"""


class Routes:
    """
    This class provides "type-safe" routes for passing messages around ZMQ.
    """
    box_measurement_rate_request: str = "BoxMeasurementRateRequest"
    box_measurement_rate_response: str = "BoxMeasurementRateResponse"
    heartbeat: str = "heartbeat"
    gc_stat: str = "gc_stat"
    box_optimization_request: str = "BoxOptimizationRequest"
    windowed_frequency: str = "windowed_frequency"
    laha_gc: str = "laha_gc"
    rms_windowed_voltage: str = "RmsWindowedVoltage"
    adc_samples: str = "AdcSamples"
    raw_voltage: str = "RawVoltage"
    makai_event: str = "MakaiEvent"
    thd_request_event: str = "ThdRequestEvent"
    threshold_optimization_request: str = "ThresholdOptimizationRequest"
    trigger_request: str = "TriggerRequest"
    annotation_request: str = "AnnotationRequest"
