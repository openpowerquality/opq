# OPQMauka Installation

## Prerequisites

First, install the [prerequisites](../installation-prerequisites.html).

## Install Python

OPQ Mauka requires version XX of Python, available [here ??](??).

## Compile the OPQMauka ZMQ broker

1. Run ```make``` in the ```mauka/MaukaBroker``` directory
2. Set MaukaBroker to run as a service and start the service

## Install the Python dependencies

1. Use pip to automatically install the dependecies for this project by referencing the ```mauka/requirements.txt``` file
```
pip install -r requirements.txt
```

## Run OPQMauka

1. Either create a service or run OpqMauka.py in a screen or tmux session
2. Don't forget to pass a configuration file as a first argument when running
```
python OpqMauka.py config.json
```

## Regarding protobuf

OPQMauka will always keep a compiled version of the protobuf library in the repo and up-to-date. This way when you pull from github or download a release, you don't need to worry about installing or compiling protobuf yourself.
