# Migrating from original data model to documented one at
# https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html

# Migration plan

# measurements
# 1. Rename device_id -> box_id

# opq_boxes
# 1. Create opq_boxes collection
# 2. Create documents for all current known boxes, fill updated values with known valuesx
# 3. Move calibration constants from CalibrationConstants collections into opq_boxes collection

# events
# 1. Rename event_number -> event_id
# 2. Rename time_stamp -> latencies
# 3. Remove boxes_received
# 4. Remove event_start
# 5. Remove event_end

# box_events
# 1. Populate box_events from original data collection
# 2. Rename event_number -> event_id
# 3. Rename time_stamp -> latencies
# 4. Rename data -> data_fs_filename

# fs.files
# 1. Add metadata.event_id
# 2. Add metadata.box_id


pass