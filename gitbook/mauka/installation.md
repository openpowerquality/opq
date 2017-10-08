# OPQMauka Installation

## Prerequisites

First, install the [prerequisites](../installation-prerequisites.html).

## Install Python

OPQ Mauka requires version **3.5 or greater** of Python. It's suggested that you use your distribution's package manager to install Python 3.5 or greater if its available. Python 3.5 or greater can also be downloaded [here](https://www.python.org/).

## Install the Python dependencies

1. Use pip to automatically install the dependencies for this project by referencing the ```mauka/requirements.txt``` file
```
pip install -r requirements.txt
```

## Install the OPQ Mauka service (Debian based systems)
If you would like Mauka to start at boot, you must create a service for it. This documentation assumes that SysVinit is used and the start-stop-daemon binary is available (most modern Debian based distributions).

1. Run the script ```util/mauka/mauka-install.sh``` as root
2. The service will now start automatically at boot
3. To start the service type ```sudo service mauka start```
4. To stop the service type ```sudo service mauka stop```
5. To restart the service type ```suer service mauka restart```


*Note: If you successfully create services for OS X or systemd, please let us know!*

## Running OPQ Mauka (non-Debian based systems)
1. Run ```mauka/OpqMauka.py```
```
# Enter the opq/mauka directory
cd mauka

# Run Mauka
python3 OpqMauka.py path_to_config.json

```

## Testing OPQ Mauka

## Regarding protobuf
Users do not need to compile protobuf for this component. The Mauka Python protobuf wrapper will be kept up to date with the source by the maintainers.
