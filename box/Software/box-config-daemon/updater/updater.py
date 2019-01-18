import subprocess


def install_latest(updates_endpoint: str):
    with open("box_update.log", "w") as fout:
        subprocess.run(["bash", "updater.sh", updates_endpoint], stdout=fout, stderr=fout)
