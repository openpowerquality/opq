import json
import argparse
import zmq
import protobuf.opq_pb2
from requests import get
from time import ctime
from time import sleep
from time import time
from threading import Thread
from threading import Lock
from pymongo import MongoClient

def generate_log_msg(service, service_id, status, info):
    serv = 'service: ' + service
    id = 'service id: ' + service_id
    stat = 'status: ' + status
    info = 'info: ' + info

    return ' '.join([ctime(), serv, id, stat, info])

def write_to_log(file_name, message):
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

def check_health(config, log_file):
    sleep_time = config['interval']
    while True:
        message = generate_log_msg('HEALTH', '', 'UP', '')
        write_to_log(log_file, message)
        sleep(sleep_time)

def check_view(config, log_file):
    sleep_time = config['interval']
    url = config['url']
    while True:
        status = get(url).status_code
        if status != 200:
            message = generate_log_msg('VIEW', '', 'DOWN', str(status))
            write_to_log(log_file, message)
        else:
            message = generate_log_msg('VIEW', '', 'UP', str(status))
            write_to_log(log_file, message)
        sleep(sleep_time)

# Global variable for asynch logging
boxes = {}
lock = Lock()

def log_boxes(sleep_time, log_file):
    while True:
        sleep(sleep_time)
        lock.acquire()
        for id, box_t_ms in boxes.items():
            time_elapsed = time() - (box_t_ms / 1000)
            if time_elapsed > 60:
                message = generate_log_msg('BOX', str(id), 'DOWN', '')
            else:
                message = generate_log_msg('BOX', str(id), 'UP', '')
            write_to_log(log_file, message)
        lock.release()


def check_boxes(config, port, log_file):
    sleep_time = config['interval']
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.connect(port)

    for box in config['boxdata']:
        # Add each box id as a new key
        boxes[box['boxID']] = 0

    box_log_thread = Thread(target=log_boxes, args=(sleep_time,log_file, ))
    box_log_thread.start()

    while True:
        measurement = socket.recv_multipart()
        trigger_message = protobuf.opq_pb2.TriggerMessage()
        trigger_message.ParseFromString(measurement[1])
    
        lock.acquire()
        if trigger_message.id in boxes:
            boxes[trigger_message.id] = trigger_message.time
        lock.release()

    box_log_thread.join()

def check_mongo(config, log_file):
    sleep_time = config['interval']
    mongo_uri = config['url']

    while True:
        client = MongoClient(mongo_uri)
        db = client['opq']
        collection = db['measurements']
        try:
            collection.find_one()
            message = generate_log_msg('MONGO', '', 'UP', 'opq/measurements')
        except:
            message = generate_log_msg('MONGO', '', 'DOWN', 'opq/measurements')
        client.close()
        write_to_log(log_file, message)
        sleep(sleep_time)


def main(config_file, log_file):
    health_config = file_to_dict(config_file)

    health_health_config = health_config[6]
    health_thread = Thread(target=check_health, args=(health_health_config,log_file, ))
    health_thread.start()

    view_config = health_config[4]
    view_thread = Thread(target=check_view, args=(view_config,log_file, ))
    view_thread.start()

    box_config = health_config[1]
    zmq_port = health_config[0]['port']
    box_thread = Thread(target=check_boxes, args=(box_config,zmq_port,log_file, ))
    box_thread.start()

    mongo_config = health_config[5]
    mongo_thread = Thread(target=check_mongo, args=(mongo_config,log_file, ))
    mongo_thread.start()
    
    health_thread.join()
    view_thread.join()
    box_thread.join()
    mongo_thread.join()

def parse_cmd_args():
    parser = argparse.ArgumentParser(description='Get config and log file names')
    parser.add_argument('-config', nargs=1, help='Name of config file', default=['config.json'])
    parser.add_argument('-log', nargs=1, help='Name of log file', default=['log.txt'])
    args = parser.parse_args()
    return args.config[0], args.log[0]

if __name__ == '__main__':
    config_file, log_file = parse_cmd_args()
    print('... reading configuration information from ' + config_file)
    print('... writing out health status to ' + config_file)
    main(config_file, log_file)
