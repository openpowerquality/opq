# OPQ Data Model

## Overview {#overview}

At the core of the OPQ system lies a centralized MongoDB database. OPQMauka and OPQMakai both primarily act as producers of data, while OPQView is solely a consumer of data.
The following section will provide a high-level overview of OPQ's data model.

## Data Model

The OPQ system utilizes the following collections:
* Measurements - Provides low-fidelity OPQBox data
* Events - Provides event meta data
* Data - Provides high-fidelity event data
* Fs.Files - Internal to GridFS filesystem (file meta-data)
* Fs.Chunks - Internal to GridFS filesystem (file binary data)


### Measurements

* _id: ObjectId
* device_id: String
* timestamp_ms: Integer
* voltage: Float
* frequency: Float

### Events

* _id: ObjectId
* type: String
* event_number: Integer
* description: String
* boxes_triggered: [Integer]
* boxes_received: [Integer]
* event_start: Integer
* event_end: Integer
* timestamp: [Integer]

### Data

* _id: ObjectId
* event_number: Integer
* box_id: Integer
* event_start: Integer
* event_end: Integer
* timestamp: [Integer]
* data: String (Note: This string references the GridFS filename that holds the actual event data)

### Fs.Files
* _id: ObjectId
* filename: String
* length: Integer
* chunkSize: Integer
* uploadDate: Date
* md5: String

### Fs.Chunks
* _id: ObjectId
* files_id: ObjectId
* n: Integer
* data: BinData