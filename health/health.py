import json
import argparse
from requests import get
from time import ctime
from time import sleep

def write_file(file_name, message):
    try:
        with open(file_name, 'a') as log_file:
            log_file.write(message + '\n')
    except:
        print('Unable to write to ' + file_name)
        exit()

def file_to_dict(file_name):
    try:
        with open(file_name) as opened_file:
            json_data = json.load(opened_file)
            return json_data
    except:
        print('Unable to open ' + file_name)
        exit()

def run_view(config, log_file):
    sleep_time = config['interval']
    url = config['url']
    while True:
        status = get(url).status_code
        if status != 200:
            message = ctime() + ' View Health Error: Status Code ' + str(status)
            write_file(log_file, message)
        else:
            message = ctime() + ' View Healthy: Status Code ' + str(status)
            write_file(log_file, message)
        sleep(sleep_time)

def main(config_file, log_file):
    config = file_to_dict(config_file)
    view_config = config[4]
    run_view(view_config, log_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='test')
    parser.add_argument('-config', nargs=1, help='Name of config file', default=['config.json'])
    parser.add_argument('-log', nargs=1, help='Name of log file', default=['log.txt'])
    args = parser.parse_args()
    main(args.config[0], args.log[0])
