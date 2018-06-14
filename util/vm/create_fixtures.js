var conn = new Mongo();
var db = conn.getDB("opq");

db.opq_boxes.insert({
    "box_id": "0",
    "name": "sim-box-0",
    "description": "sim-box-0",
    "calibration_constant": 152.0,
    "location": "null-island",
    "location_start_time_ms": 1529014620000,
    "location_archive": []
});

db.locations.insert({
    "slug": "null-island",
    "coordinates": [0.0, 0.0],
    "description": "simulated null island"
});