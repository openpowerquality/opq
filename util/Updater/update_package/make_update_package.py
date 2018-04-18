import argparse
import json
import os
import shutil
import subprocess
import tarfile
import time
import typing


def read_version(version_file: str) -> typing.Dict:
    with open(version_file, "r") as fin:
        return json.load(fin)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("update", help="Path to update script to distribute")

    parser.add_argument("--dist-dir",       "-d", default="/var/www/opq.box.updater")
    parser.add_argument("--version-file",   "-v", default="/var/www/opq.box.updater/version.json")
    parser.add_argument("--private-key",    "-k", default="/etc/opq/curve/signing_keys/opq-signing-private.pem")
    parser.add_argument("--signing-script", "-s", default="/usr/local/bin/opq/opq-sign.sh")

    args = parser.parse_args()
    print(args)
    version_conf = read_version(args.version_file)
    print(version_conf)

    # First, let's make a tmp directory to work with
    os.makedirs("tmp/", exist_ok=True)

    # Copy script over
    shutil.copyfile(args.update, "tmp/update.sh")
    os.chdir("tmp")

    # Compress
    with tarfile.open(version_conf["package"], "w:gz") as fout:
        fout.add("update.sh")

    # Sign
    subprocess.call(["bash", args.signing_script, args.private_key, version_conf["package"]])

    # Distribute
    shutil.copyfile(version_conf["package"], args.dist_dir + "/" + version_conf["package"])
    shutil.copyfile(version_conf["signature"], args.dist_dir + "/" + version_conf["signature"])

    # Update version info
    version_conf["version"] = version_conf["version"] + 1
    version_conf["release"] = int(time.time())

    with open(args.version_file, "w") as fout:
        json.dump(version_conf, fout)

    os.chdir("..")
    shutil.rmtree("tmp")
