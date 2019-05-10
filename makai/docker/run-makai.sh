#!/bin/bash

/build/bin/ab ACQUISITION_BROKER_SETTINGS &
/build/bin/tb TRIGGERING_BROKER_SETTINGS &
/build/bin/event_service &
/build/bin/makai
