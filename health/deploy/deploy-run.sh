#!/bin/bash

# This is the normal way to start up OPQHealth
nohup python2 health.py > logfile.txt 2>&1 &
