import argparse
import json
import os.path
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import gridfs
import numpy as np
import pymongo
import pymongo.database

OPQ_DB = "opq"
INCIDENTS_COLL = "incidents"


def make_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def null_or_empty(s: str) -> bool:
    return s is None or len(s) == 0


def load_waveform(grid_fs: gridfs.GridFS,
                  gridfs_path: str) -> np.ndarray:
    data_bytes: bytes = grid_fs.find_one({"filename": gridfs_path}).read()
    waveform: np.ndarray = np.frombuffer(data_bytes, np.int16)

    return waveform


def store_incident(incident_doc: Dict,
                   out_dir: str,
                   grid_fs: gridfs.GridFS,
                   box_events_coll: pymongo.collection.Collection,
                   events_coll: pymongo.collection.Collection):

    # Setup Incident directory structure
    incident_id: str = str(incident_doc["incident_id"])
    box_id: str = incident_doc["box_id"]
    dir_path: str = os.path.join(out_dir, incident_id)
    make_dir(dir_path)

    # Store Incident metadata
    metadata_out_path: str = os.path.join(dir_path, f"incident_{incident_id}_{box_id}.json")
    with open(metadata_out_path, "w") as fout:
        json.dump(incident_doc, fout)

    # Store Incident waveform
    incident_gridfs_filename = incident_doc["gridfs_filename"]

    if not null_or_empty(incident_gridfs_filename):
        incident_waveform: np.ndarray = load_waveform(grid_fs, incident_gridfs_filename)
        incident_waveform_path: str = os.path.join(dir_path, f"incident_{incident_id}.npy")
        np.save(incident_waveform_path, incident_waveform)

    # Store Box Event data
    box_id: str = incident_doc["box_id"]
    event_id: int = incident_doc["event_id"]
    if event_id > 0:
        # Box event metadata
        box_event_query: Dict = {"event_id": event_id, "box_id": box_id}
        box_event_projection: Dict[str, bool] = {"_id": False}
        box_event: Dict = box_events_coll.find_one(box_event_query, projection=box_event_projection)

        if box_event is not None:
            box_event_metadata_path: str = os.path.join(dir_path, f"box_event_{event_id}_{box_id}.json")
            with open(box_event_metadata_path, "w") as event_metadata_out:
                json.dump(box_event, event_metadata_out)

            # Box event waveform
            box_event_gridfs_filename: str = box_event["data_fs_filename"]
            if not null_or_empty(box_event_gridfs_filename):
                event_waveform: np.ndarray = load_waveform(grid_fs, box_event_gridfs_filename)
                event_waveform_path: str = os.path.join(dir_path, f"box_event_{event_id}_{box_id}.npy")
                np.save(event_waveform_path, event_waveform)

        # Event metadata
        event: Dict = events_coll.find_one({"event_id": event_id}, projection={"_id": False})
        if event is not None and len(event.keys()) > 0:
            event_metadata_path: str = os.path.join(dir_path, f"event_{event_id}_{box_id}.json")
            with open(event_metadata_path, "w") as event_out:
                json.dump(event, event_out)


def store_incident_data(mongo_client: pymongo.MongoClient,
                        out_dir: str) -> None:
    db: pymongo.database.Database = mongo_client[OPQ_DB]
    incidents_coll: pymongo.collection.Collection = db[INCIDENTS_COLL]
    box_events_coll: pymongo.collection.Collection = db["box_events"]
    events_coll: pymongo.collection.Collection = db["events"]

    grid_fs: gridfs.GridFS = gridfs.GridFS(db)

    incidents_query: Dict = {"start_timestamp_ms": {"$gte": 1571803542270}}
    incidents_projection: Dict[str, bool] = {"_id": False}

    incidents_cursor: pymongo.cursor.Cursor = incidents_coll.find(incidents_query, projection=incidents_projection)
    incident_docs: List[Dict] = list(incidents_cursor)

    total_docs: int = len(incident_docs)
    for i, incident_doc in enumerate(incident_docs):
        print(i, total_docs, float(i) / total_docs * 100.0)
        try:
            store_incident(incident_doc, out_dir, grid_fs, box_events_coll, events_coll)
        except Exception as e:
            print(f"error: {str(e)}")


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument("out_dir")

    args = parser.parse_args()

    out_dir: str = args.out_dir
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()

    store_incident_data(mongo_client, out_dir)


if __name__ == "__main__":
    main()
