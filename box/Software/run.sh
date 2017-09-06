#!/usr/bin/env/bash
tmux new-session -s opq 'python Acquisition/acquisition.py template.set' \; \
    split-window './Triggering/build/Triggering template.set' \; \
    select-layout even-vertical

