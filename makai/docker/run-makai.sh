#!/bin/bash

/build/bin/AcquisitionBroker ACQUISITION_BROKER_SETTINGS &
/build/bin/TriggeringBroker TRIGGERING_BROKER_SETTINGS &
/build/bin/makai