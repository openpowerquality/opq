import sys
sys.path.append("../util")
import json_util
import urllib.request

def main():
    local_file_name = 'old_version.json'
    server_file_name = 'new_version.json'
    local_version = get_local_version(local_file_name)
    updated_version = get_updated_version(server_file_name)
    compare_local_to_updated(local_version, updated_version)

def compare_local_to_updated(local_version, updated_version):
    has_latest_version = is_updated_version(local_version, updated_version)
    print_update_results(has_latest_version)

def get_updated_version(file_name):
    url = 'http://127.0.0.1:8080/updates/' + file_name
    response = urllib.request.urlopen(url)
    response_as_dict = json_util.http_response_to_dict(response)
    return response_as_dict

def get_local_version(file_name):
    local_version = json_util.file_to_dict(file_name)
    return local_version

def print_update_results(has_latest_version):
    if has_latest_version:
        print("Already has latest version")
    else:
        print("Does not have latest version")

def is_updated_version(local_version, updated_version):
    if not 'version' in local_version:
        return False
    elif not 'version' in updated_version:
        return False
    elif local_version['version'] < updated_version['version']:
        return False
    else:
        return True

if __name__ == '__main__':
    main()
