from mongo.mongo import get_box_calibration_constants

SAMPLES_PER_CYCLE = 200.0
SAMPLE_RATE_HZ = 12000.0

def get_calibration_constant(box_id: int) -> float:
    calibration_constants = get_box_calibration_constants()
    if box_id in calibration_constants:
        return calibration_constants[box_id]
    else:
        return 1.0