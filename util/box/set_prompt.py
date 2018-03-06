"""
This script will format a bash prompt for an OPQ box.

The prompt will have the form of:

    box_id@local_ip:~/cwd [time date]
    >


This script should be included in the box's .bashrc in the following way:

PS1=$(python3 /path/to/set_prompt.py)

"""

import json
import socket
import typing


def read_config(path: str) -> typing.Dict:
    with open(path, "r") as fin:
        return json.load(fin)


def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.0.0.8', 1027))
    except socket.error:
        return None
    return s.getsockname()[0]


def format_prompt(box_id: str, local_ip: str) -> str:
    return '\\n{}@{}:\w [\\t \d]\\n> '.format(box_id, local_ip)


if __name__ == "__main__":
    settings_path = "/etc/opq/settings.json"
    config = read_config(settings_path)
    box_id = str(config["box_id"])
    local_ip = my_ip()
    ps1 = format_prompt(box_id, local_ip)
    print(ps1)
