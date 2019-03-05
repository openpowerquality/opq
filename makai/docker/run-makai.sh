#!/bin/bash

/build/bin/AcquisitionBroker /build/conf/acquisition_broker.config.json &
/build/bin/TriggeringBroker /build/conf/triggering_broker.config.json &
/build/bin/makai