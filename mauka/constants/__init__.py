from mongo.mongo import get_box_calibration_constants

SAMPLES_PER_CYCLE = 200.0
SAMPLE_RATE_HZ = 12000.0
CALIBRATION_CONSTANTS = get_box_calibration_constants()

def get_calibration_constant(box_id: int) -> float:
    if box_id in CALIBRATION_CONSTANTS:
        return CALIBRATION_CONSTANTS[box_id]
    else:
        return 1.0