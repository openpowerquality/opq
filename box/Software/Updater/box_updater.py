import urllib.request
import subprocess
from os import remove
from os import path
from os import makedirs
import json
import tarfile
import logging
import traceback

# Set default logging format and options
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', \
    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

def main():
    logging.info('main()')

    version_file, public_key, update_package, signature = set_config('/etc/opq/updater_config.json')

    check_download_path()

    if (is_latest_version(version_file)):
        logging.info('Box already up to date')
        quit()

    download_files(public_key, update_package, signature)

    is_verified = verify_package(public_key, update_package, signature, version_file)

    if is_verified:
        open_package(update_package)
        run_update()
    else:
        logging.error('Unable to verify package')

# Read config.json to get file names and download path
def set_config(file_name):
    logging.info('set_config(%s)', file_name)
    try:
        config_json = file_to_dict(file_name)
        global download_dir_path
        download_dir_path = config_json['download_dir_path']
        global server_url
        server_url = config_json['server_url']

        # Read version.json from emilia
        version_file_name = config_json['version_file']
        public_key, update_package, signature = get_file_names_from(version_file_name)
        return version_file_name, public_key, \
            update_package, signature
    except Exception as e:
        logging.exception(e)
        quit()

# Downloads and reads version.json from emilia to get update file names
def get_file_names_from(file_name):
    logging.info('get_file_names(%s)', file_name)
    download_file_from_emilia(file_name)
    version_file = file_to_dict(download_dir_path + file_name)
    public_key = version_file['public_key']
    update_package = version_file['package']
    signature = version_file['signature']
    return public_key, update_package, signature



# Checks if download_dir_path exists -> build it if not
def check_download_path():
    logging.info('check_download_path(): ' + download_dir_path)
    if not path.exists(download_dir_path):
        makedirs(download_dir_path)

# Downloads version file from server
# Compares compares local and server version numbers
# Note - If local version file not found -> run update
# Note - Also checks if dict fields were expected
# Note - If expected fields not found, returns false or exits program
def is_latest_version(version_file):
    logging.info('is_latest_version(%s)', version_file)
    download_file_from_emilia(version_file)
    server_version = file_to_dict(download_dir_path + version_file)
    local_version = file_to_dict(download_dir_path + 'local_version.json')
    # local version is invalid or doesn't exist -> run update
    if not local_version or not 'version' in local_version:
        return False
    # Server version is invalid -> don't update
    elif not server_version or not 'version' in server_version:
        logging.error('Server %s has invalid format or does not exist', version_file)
        quit()
    elif local_version['version'] < server_version['version']:
        return False
    return True

# Downloads public_key, update_package, signature
def download_files(public_key, update_package, signature):
    logging.info('download_files(%s, %s, %s)' % (public_key, update_package, signature))
    download_file_from_emilia(public_key)
    download_file_from_emilia(update_package)
    download_file_from_emilia(signature)

# Sends http request for file, as well as error handling
def download_file_from_emilia(file_name):
    logging.info('download_file_from_emilia(%s)', file_name)
    try:
        url = server_url + file_name
        urllib.request.urlretrieve(url, download_dir_path + file_name)
    except Exception as e:
        logging.exception(e)
        quit()

# Runs ssl script to verify package
# Renames downloaded version file to local_version for use by next update
def verify_package(public_key, update_package, signature, version_file):
    logging.info('verify_package(%s, %s, %s)' % (public_key, update_package, signature))
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

        # ssl script returns this string if success
        if 'Verified OK' in str(verified):
            return True
        return False
    except Exception as e:
        logging.exception(e)
        quit()

# Opens the tar package and handles errors
def open_package(update_package):
    logging.info('open_package(%s)',update_package)
    try:
        with tarfile.open(download_dir_path + update_package) as tar:
            tar.extractall(download_dir_path)
    except Exception as e:
        logging.exception(e)
        quit()

# Calls/runs the shell script file
def run_update():
    logging.info('run_update()')
    try:
        subprocess.call(download_dir_path + 'update.sh')
    except Exception as e:
        logging.exception(e)
        quit()

# Returns .json file as a dict
def file_to_dict(file_name):
    try:
        with open(file_name) as opened_file:
            json_data = json.load(opened_file)
            return json_data
    except:
        return {}

# Turns http response obj into dict
def http_response_to_dict(response):
    data = json.loads(response.read().decode(response.info().get_param('charset')  \
        or 'utf-8'))
    return data

if __name__ == '__main__':
    main()
