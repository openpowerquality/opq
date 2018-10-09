"""
Rerun incidents from previous events.
"""

import multiprocessing

import mongo

import plugins.makai_event_plugin


def rerun_incidents():
    """
    Rerun incidents from previous events.
    """
    opq_mongo_client = mongo.OpqMongoClient()

    # Drop all old incidents
    print("Dropping incidents collection... ", end="")
    opq_mongo_client.incidents_collection.drop()
    print("Done.")

    # Remove files from grid_fs
    print("Removing files from gridfs... ", end="")
    total_files = opq_mongo_client.get_collection("fs.files").count({"metadata.incident_id": {"$exists": True}})
    i = 0
    for gridfs_file in opq_mongo_client.gridfs.find({"metadata.incident_id": {"$exists": True}}):
        if i % 5000 == 0:
            print("\rRemoving files from gridfs... [{}/{}] {}%".format(i, total_files, (i / total_files) * 100), end="")
        # pylint: disable=W0212
        # noinspection PyProtectedMember
        opq_mongo_client.gridfs.delete(gridfs_file._id)
        i += 1
    print("Done.")

    print("Rebuilding incidents... ", end="")
    event_waveforms_query = {"metadata.event_id": {"$exists": True},
                             "length": {"$gt": 0}}

    event_files = opq_mongo_client.get_collection("fs.files").find(event_waveforms_query,
                                                                   ["metadata.event_id", "length"])
    event_ids = list(set([event_file["metadata"]["event_id"] for event_file in event_files]))
    event_ids.sort()

    pool = multiprocessing.Pool(6)

    i = 0
    for _ in pool.imap(plugins.makai_event_plugin.rerun, event_ids):
        if i % 10 == 0:
            print("\rRebuilding incidents... {}/{} {}%".format(i, len(event_ids), (i / len(event_ids)) * 100), end="")

        i += 1
    print("Done.")


if __name__ == "__main__":
    rerun_incidents()
