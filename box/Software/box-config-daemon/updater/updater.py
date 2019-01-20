import os
import subprocess


def install_latest(updates_endpoint: str):
    os.makedirs("/var/log/opq", exist_ok=True)
    with open("/var/log/opq/box_update.log", "w") as fout:
        subprocess.run(["bash", "/usr/local/box-config-daemon/updater/updater.sh", updates_endpoint], stdout=fout, stderr=fout)
