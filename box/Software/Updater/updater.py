import urllib.request
import subprocess
from os import remove
from os import path
from os import makedirs
import json_util
import tarfile

download_dir_path = '/var/opq/updater'
version_file = 'version.json'
public_key = 'opq-signing-public.pem'
update_package = 'opq.box.updates.tar.gz'
signature = 'opq.box.updates.tar.gz.sig'

def main():
    check_download_path()

    if (is_latest_version(version_file)):
        print('Box already up to date')
        quit()

    download_files(public_key, update_package, signature)

    is_verified = verify_package(public_key, signature, update_package)

    if is_verified:
        open_package(update_package)
        run_update()
    else:
        print('Error: Unable to verify package')

def check_download_path():
    if not path.exists(download_dir_path):
        makedirs(download_dir_path)

def is_latest_version(version_file):
    download_file_from_emilia(version_file)
    server_version = json_util.file_to_dict(download_dir_path + version_file)
    local_version = json_util.file_to_dict(download_dir_path + 'local_version.json')
    # local version is invalid or doesn't exist -> run update
    if not local_version or not 'version' in local_version:
        return False
    # Server version is invalid -> don't update
    elif not server_version or not 'version' in server_version:
        print('Server version has invalid format or does not exist')
        return True
    elif local_version['version'] < server_version['version']:
        return False
    return True

def download_files(public_key, update_package, signature):
    download_file_from_emilia(public_key)
    download_file_from_emilia(update_package)
    download_file_from_emilia(signature)

def download_file_from_emilia(file_name):
    try:
        url = 'http://emilia.ics.hawaii.edu:8151/' + file_name
        urllib.request.urlretrieve(url, download_dir_path + file_name)
    except Exception as e:
        print('Error downloading \'' + file_name + '\': ' + str(e))
        quit()

def verify_package(public_key, signature, update_package):
    try:
        subprocess.call(['openssl', 'base64', '-d', \
            '-in', download_dir_path + signature, \
            '-out', download_dir_path + signature + '.bin'])
        verified = subprocess.check_output(['openssl', 'dgst', \
            '-sha256', '-verify', \
            download_dir_path + public_key, '-signature', \
            download_dir_path + signature + '.bin', \
            download_dir_path + update_package])
        remove(download_dir_path + signature + '.bin')

        # rename downloaded 'version.json' as 'local_version.json'
        subprocess.call(['mv', download_dir_path + version_file, \
            download_dir_path + 'local_version.json'])

        if 'Verified OK' in str(verified):
            return True
        return False
    except Exception as e:
        print('Error verifying package: ' + str(e))
        quit()

def open_package(update_package):
    try:
        with tarfile.open(download_dir_path + update_package) as tar:
            tar.extractall(download_dir_path)
            print('Extracted package')
    except Exception as e:
        print('Error opening package: ' + str(e))
        quit()

def run_update():
    try:
        subprocess.call(download_dir_path + 'update.sh')
    except Exception as e:
        print('Error running update: ' + str(e))

if __name__ == '__main__':
    main()
