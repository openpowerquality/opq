#!/bin/bash

# This is the normal way to start up OPQHealth
nohup python3 -u health.py > nohupout.txt 2>&1 &
