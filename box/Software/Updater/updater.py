import urllib.request
import subprocess
from os import remove
import json_util
import tarfile

# def run_script_file(relative_path):
#     exec(open(relative_path).read())
# TODO - Putting ./downloads in front of everything is kind of a bummer
# TODO - Should I just download everything into current directory?

def main():
    version_file = 'version.json'
    # True if already up to date
    if (check_for_update(version_file)):
        print('Already up to date')
        quit()

    public_key = 'opq-signing-public.pem'
    update_package = 'opq.box.updates.tar.gz'
    signature = 'opq.box.updates.tar.gz.sig'

    download_files(public_key, update_package, signature)

    verified = verify_package(public_key, signature, update_package)

    if verified:
        open_package(update_package)
        run_update()
    else:
        print('Unable to verify package')

def check_for_update(version_file):
    download_file_from_emilia(version_file)
    new_version = json_util.file_to_dict('./downloads/' + version_file)
    # NOTE Temporarily hardcoded local version file name
    # TODO Returns empty dict if not found, should probably change this?
    current_version = json_util.file_to_dict('./downloads/current_version.json')
    return has_updated_version(current_version, new_version)

def has_updated_version(current_version, new_version):
    # add null safety
    if current_version['version'] < new_version['version']:
        return False
    else:
        return True

def download_files(public_key, update_package, signature):
    download_file_from_emilia(public_key)
    download_file_from_emilia(update_package)
    download_file_from_emilia(signature)

def download_file_from_emilia(file_name):
    # TODO Currently downloading everything to /downloads
    try:
        url = 'http://emilia.ics.hawaii.edu:8151/' + file_name
        urllib.request.urlretrieve(url, './downloads/' + file_name)
    except Exception as e:
        print("Error downloading \"" + file_name + "\": " + str(e))
        quit()

# TODO catch errors/output for subprocess
def verify_package(public_key, signature, update_package):
    subprocess.call(['openssl', 'base64', '-d', \
        '-in', './downloads/' + signature, \
        '-out', './downloads/' + signature + '.bin'])
    verified = subprocess.check_output(['openssl', 'dgst', \
        '-sha256', '-verify', \
        './downloads/' + public_key, '-signature', \
        './downloads/' + signature + '.bin', \
        './downloads/' + update_package])
    remove('./downloads/' + signature + '.bin')

    if 'Verified OK' in str(verified):
        return True
    return False

def open_package(update_package):
    try:
        with tarfile.open('./downloads/' + update_package) as tar:
            tar.extractall("./downloads")
            #tar.extractall()
            #print("Success!")
    except Exception as e:
        print(e)

def run_update():
    subprocess.call('./downloads/update.sh')

if __name__ == '__main__':
    main()
