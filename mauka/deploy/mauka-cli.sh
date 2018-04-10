#!/bin/bash

# Convenience shortcut for accessing mauka command line interface

cd /usr/local/bin/opq/mauka
python3 -m plugins.manager /etc/opq/mauka/config.json
