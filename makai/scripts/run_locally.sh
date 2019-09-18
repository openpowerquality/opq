#!/bin/bash

MAKAI_CONFIG_DIR=/etc/opq/makai

/usr/local/bin/ab ${MAKAI_CONFIG_DIR}/acquisition_broker.config.json &
/usr/local/bin/tb ${MAKAI_CONFIG_DIR}/triggering_broker.config.json &
/usr/local/bin/event_service ${MAKAI_CONFIG_DIR}/makai.config.json &
/usr/local/bin/makai ${MAKAI_CONFIG_DIR}/makai.config.json