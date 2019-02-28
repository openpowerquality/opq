#!/bin/bash

/build/bin/AcquisitionBroker /build/conf/acquisition_broker_config.json &
/build/bin/TriggeringBroker /build/conf/triggering_broker_config.json &
/build/bin/makai /build/conf/makai/makai.json &