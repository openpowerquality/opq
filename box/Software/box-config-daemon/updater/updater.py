import subprocess


def install_latest(updates_endpoint: str):
    with open("/usr/local/box-config-daemon/updater/box_update.log", "w") as fout:
        subprocess.run(["bash", "/usr/local/box-config-daemon/updater/updater.sh", updates_endpoint], stdout=fout, stderr=fout)
