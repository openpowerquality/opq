var conn = new Mongo();
var db = conn.getDB("opq");

/* box_events */
var box_events = db.box_events;
box_events.createIndex({"event_id": 1});
box_events.createIndex({"box_id": 1});
box_events.createIndex({"event_id": 1, "box_id": 1}, {"unique": true});
box_events.createIndex({"event_start_timestamp_ms": 1, "box_id": 1});

/* box_owners */
var box_owners = db.box_owners;
box_owners.createIndex({"username": 1});
box_owners.createIndex({"box_id": 1}, {"unique": true});

/* events */
var events = db.events;
events.createIndex({"event_id": 1}, {"unique": true});
events.createIndex({"target_event_start_timestamp_ms": 1});

/* health */
var health = db.health;
health.createIndex({"timestamp": 1});

/* incidents */
var incidents = db.incidents;
incidents.createIndex({"incident_id": 1}, {"unique": true});
incidents.createIndex({"start_timestamp_ms": 1});

/* locations */
var locations = db.locations;
locations.createIndex({"slug": 1}, {"unique": 1});
locations.createIndex({"description": 1}, {"unique": 1});
locations.createIndex({"coordinates": "2d"});

/* measurements */
var measurements = db.measurements;
measurements.createIndex({"box_id": 1, "timetstamp_ms": 1}, {"unique": true});
measurements.createIndex({"expireAt": 1}, {"expireAfterSeconds": 0});

/* opq_boxes */
var opq_boxes = db.opq_boxes;
opq_boxes.createIndex({"box_id": 1}, {"unique": true});
opq_boxes.createIndex({"name": 1}, {"unique": true});

/* regions */
var regions = db.regions;

/* system_stats */
var system_stats = db.system_stats;

/* trends */
var trends = db.trends;
trends.createIndex({"box_id": 1, "timestamp_ms": 1});

/* users */
var users = db.users;
users.createIndex({"username": 1}, {"unique": true});


