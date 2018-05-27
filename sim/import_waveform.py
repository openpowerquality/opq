import gridfs
import numpy
import pymongo

if __name__ == "__main__":
    import sys
    waveform_file = sys.argv[1]
    gridfs_fn = sys.argv[2]

    with open(waveform_file, "r") as f:
        samples = numpy.array(list(map(lambda line: int(line.strip()), f.readlines())), dtype=numpy.dtype('i2'))
        data = samples.tobytes()

        client = pymongo.MongoClient()
        db = client["opq"]
        fs = gridfs.GridFS(db)

        fs.put(data, filename=gridfs_fn)
