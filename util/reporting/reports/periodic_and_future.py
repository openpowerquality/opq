from typing import Dict, List, Optional

import pymongo
import pymongo.database


def periodic_incidents_identified(start_ts_s: int,
                                  end_ts_s: int,
                                  mongo_client: pymongo.MongoClient,
                                  for_box: Optional[str] = None) -> int:
    db: pymongo.database.Database = mongo_client["opq"]
    phenomena_coll: pymongo.collection.Collection = db["phenomena"]
    incidents_coll: pymongo.collection.Collection = db["incidents"]

    phenomena_query: Dict = {"phenomena_type.type": "periodic"}

    if for_box is not None:
        phenomena_query["affected_opq_boxes"] = for_box

    phenomena_projection: Dict[str, bool] = {
        "_id": False,
        "affected_opq_boxes": True,
        "related_incident_ids": True,
        "phenomena_type.type": True,
        "phenomena_id": True,
    }

    phenomena_cursor: pymongo.cursor.Cursor = phenomena_coll.find(phenomena_query, projection=phenomena_projection)
    phenomena_docs: List[Dict] = list(phenomena_cursor)

    incidents_projection: Dict[str, bool] = {
        "_id": False,
        "incident_id": True,
        "start_timestamp_ms": True
    }

    for phenomena_doc in phenomena_docs:
        related_incident_ids: List[int] = phenomena_doc["related_incident_ids"]
        phenomena_id: int = phenomena_doc["phenomena_id"]
        affected_opq_boxes: List[str] = phenomena_doc["affected_opq_boxes"]
        incidents_query: Dict = {"incident_id": {"$in": related_incident_ids},
                                 "start_timestamp_ms": {"$gte": start_ts_s * 1_000.0,
                                                        "$lte": end_ts_s * 1_000.0}}
        incidents_cnt: int = incidents_coll.find(incidents_query, projection=incidents_projection).count()
        print(f"phenomena_id={phenomena_id} affected_opq_boxes={affected_opq_boxes} num_incidents={incidents_cnt}")


def periodic_events_identified(start_ts_s: int,
                               end_ts_s: int,
                               mongo_client: pymongo.MongoClient,
                               for_box: Optional[str] = None) -> int:
    db: pymongo.database.Database = mongo_client["opq"]
    phenomena_coll: pymongo.collection.Collection = db["phenomena"]
    events_coll: pymongo.collection.Collection = db["events"]

    phenomena_query: Dict = {"phenomena_type.type": "periodic"}

    if for_box is not None:
        phenomena_query["affected_opq_boxes"] = for_box

    phenomena_projection: Dict[str, bool] = {
        "_id": False,
        "affected_opq_boxes": True,
        "related_event_ids": True,
        "phenomena_type.type": True,
        "phenomena_id": True,
    }

    phenomena_cursor: pymongo.cursor.Cursor = phenomena_coll.find(phenomena_query, projection=phenomena_projection)
    phenomena_docs: List[Dict] = list(phenomena_cursor)

    events_projection: Dict[str, bool] = {
        "_id": False,
        "event_id": True,
        "target_event_start_timestamp_ms": True
    }

    for phenomena_doc in phenomena_docs:
        related_event_ids: List[int] = phenomena_doc["related_event_ids"]
        phenomena_id: int = phenomena_doc["phenomena_id"]
        affected_opq_boxes: List[str] = phenomena_doc["affected_opq_boxes"]
        incidents_query: Dict = {"event_id": {"$in": related_event_ids},
                                 "target_event_start_timestamp_ms": {"$gte": start_ts_s * 1_000.0,
                                                                     "$lte": end_ts_s * 1_000.0}}
        events_cnt: int = events_coll.find(incidents_query, projection=events_projection).count()
        print(f"phenomena_id={phenomena_id} affected_opq_boxes={affected_opq_boxes} num_events={events_cnt}")

def future_counts(start_ts_s: int,
                  end_ts_s: int,
                  mongo_client: pymongo.MongoClient,):
    db: pymongo.database.Database = mongo_client["opq"]
    phenomena_coll: pymongo.collection.Collection = db["phenomena"]

    query = {
        "start_ts_ms": {"$gte": start_ts_s * 1_000.0,
                        "$lte": end_ts_s * 1_000.0},
        "phenomena_type.type": "future",
        "affected_opq_boxes": "1021"
    }

    future_docs = list(phenomena_coll.find(query))
    total_docs = len(future_docs)
    realized_docs = len(list(filter(lambda doc: doc["phenomena_type"]["realized"], future_docs)))
    print(total_docs, realized_docs, total_docs - realized_docs)

def main():
    start_ts_s: int = 1577786400
    end_ts_s: int = 1578391200
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()

    # periodic_events_identified(start_ts_s, end_ts_s, mongo_client)
    # periodic_incidents_identified(start_ts_s, end_ts_s, mongo_client)
    future_counts(start_ts_s, end_ts_s, mongo_client)


if __name__ == "__main__":
    main()
