import pymongo
import pymongo.database

import analysis
import mongo

def main():
    mongo_client = mongo.OpqMongoClient()

    query = {"classifications": {"$in": ["FREQUENCY_SAG", "FREQUENCY_SWELL"]}}

    projection = {
        "_id": False,
        "classifications": True,
        "incident_id": True,
        "event_id": True,
        "gridfs_filename": True,
        "box_id": True,
        "deviation_from_nominal": True
    }

    for incident in mongo_client.incidents_collection.find(query, projection=projection):
        waveform = mongo.get_waveform(mongo_client, incident["gridfs_filename"])
        calibration_constant = mongo_client.get_box_calibration_constant(incident["box_id"])
        waveform_calibrated = waveform / calibration_constant
        frequency_per_cycle = analysis.frequency_per_cycle(waveform_calibrated)
        print("prev dev=", incident["deviation_from_nominal"])
        if "FREQUENCY_SAG" in incident["classifications"]:
            print("new dev sag=", min(frequency_per_cycle))
        elif "FREQUENCY_SWELL" in incident["classifications"]:
            print("new dev swell=", max(frequency_per_cycle))
        else:
            pass

if __name__ == "__main__":
    main()
