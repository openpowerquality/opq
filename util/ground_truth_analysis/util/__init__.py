from typing import *

opq_box_to_uhm_meters: Dict[str, List[str]] = {
    "1000": ["POST_MAIN_1",
             "POST_MAIN_2"],
    "1001": ["HAMILTON_LIB_PH_III_CH_1_MTR",
             "HAMILTON_LIB_PH_III_CH_2_MTR",
             "HAMILTON_LIB_PH_III_CH_3_MTR",
             "HAMILTON_LIB_PH_III_MAIN_1_MTR",
             "HAMILTON_LIB_PH_III_MAIN_2_MTR",
             "HAMILTON_LIB_PH_III_MCC_AC1_MTR",
             "HAMILTON_LIB_PH_III_MCC_AC2_MTR"],
    "1002": ["POST_MAIN_1",
             "POST_MAIN_2"],
    "1003": ["KELLER_HALL_MAIN_MTR"],
    "1005": [],
    "1006": [],
    "1007": [],
    "1008": [],
    "1009": [],
    "1010": [],
    "1021": ["MARINE_SCIENCE_MAIN_A_MTR",
             "MARINE_SCIENCE_MAIN_B_MTR",
             "MARINE_SCIENCE_MCC_MTR"],
    "1022": ["AG_ENGINEERING_MAIN_MTR",
             "AG_ENGINEERING_MCC_MTR"],
    "1023": ["LAW_LIB_MAIN_MTR"],
    "1024": [],
    "1025": ["KENNEDY_THEATRE_MAIN_MTR"]
}

uhm_meter_to_opq_box: Dict[str, str] = {}
for opq_box, uhm_meters in opq_box_to_uhm_meters.items():
    for uhm_meter in uhm_meters:
        uhm_meter_to_opq_box[uhm_meter] = opq_box
