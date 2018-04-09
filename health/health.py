import json
import argparse
import zmq
import protobuf.opq_pb2
import requests
from time import ctime
from time import sleep
from time import time
from threading import Thread
from threading import Lock
from pymongo import MongoClient
from datetime import datetime

# Global valiables
g_log_file = None
lock = Lock()
boxes = {}

def get_msg_as_json(service, service_id, status, info):
    msg = {}
    msg['service'] = service
    msg['serviceID'] = str(service_id)
    msg['status'] = status
    msg['info'] = str(info)
    return msg

def save_message(message):
    write_to_log(message)
    write_to_mongo(message)

def get_log_msg(message):
    serv = 'service: ' + message['service']
    id = 'service id: ' + str(message['serviceID'])
    stat = 'status: ' + message['status']
    info = 'info: ' + message['info']

    return ' '.join([ctime(), serv, id, stat, info])

def write_to_log(message):
    log_msg = get_log_msg(message)
    try:
        with open(g_log_file, 'a') as log_file:
            log_file.write(log_msg + '\n')
    except:
        print('Unable to write to ' + g_log_file)
        exit()

def write_to_mongo(message):
    client = MongoClient()
    db = client['opq']
    coll = db['health']
  
    doc = coll.find_one({'service':message['service'],'serviceID':message['serviceID']}, sort= [('timestamp', -1)])

    message['timestamp'] = datetime.now()

    if (doc) and (doc['status'] == 'UP') and (message['status'] == 'UP'):
        # update timestamp
        coll.update_one({'_id': doc['_id']}, \
            {'$set': {'timestamp': message['timestamp']}})
    else:
        coll.insert_one(message)

    client.close()

def file_to_dict(file_name):
    try:
        with open(file_name) as opened_file:
            json_data = json.load(opened_file)
            return json_data
    except:
        print('Unable to open ' + file_name)
        exit()

def check_health(config):
    sleep_time = config['interval']
    while True:
        message = get_msg_as_json('HEALTH', '', 'UP', '')
        save_message(message)
        sleep(sleep_time)

def check_view(config):
    sleep_time = config['interval']
    url = config['url']
    while True:
        try:
            with requests.Session() as sess:
                status = sess.get(url).status_code
            if status != 200:
                message = get_msg_as_json('VIEW', '', 'DOWN', str(status))
            else:
                message = get_msg_as_json('VIEW', '', 'UP', str(status))
        except Exception as e:
            message = get_msg_as_json('VIEW', '', 'DOWN', e)
        save_message(message)
        sleep(sleep_time)

def log_boxes(sleep_time):
    while True:
        sleep(sleep_time)
        lock.acquire()
        for id, box_t_ms in boxes.items():
            time_elapsed = time() - (box_t_ms / 1000)
            if time_elapsed > 300:
                message = get_msg_as_json('BOX', str(id), 'DOWN', '')
            else:
                message = get_msg_as_json('BOX', str(id), 'UP', '')
            save_message(message)
        lock.release()

def check_boxes(config, port):
    sleep_time = config['interval']
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.connect(port)

    for box in config['boxdata']:
        # Add each box id as a new key
        boxes[box['boxID']] = 0

    box_log_thread = Thread(target=log_boxes, args=(sleep_time, ))
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

def check_mongo(config):
    sleep_time = config['interval']
    mongo_uri = config['url']

    while True:
        client = MongoClient(mongo_uri)
        db = client['opq']
        collection = db['measurements']
        try:
            collection.find_one()
            message = get_msg_as_json('MONGO', '', 'UP', 'opq/measurements')
        except:
            message = get_msg_as_json('MONGO', '', 'DOWN', 'opq/measurements')
        client.close()
        save_message(message)
        sleep(sleep_time)

def check_mauka_plugins(config_plugins, mauka_plugins):
    for plugin in config_plugins:
        if plugin in mauka_plugins:
            t_elapsed = time() - mauka_plugins[plugin]
            if t_elapsed <= 300:
                message = get_msg_as_json('MAUKA', plugin, 'UP', '')
            else:
                message = get_msg_as_json('MAUKA', plugin, 'DOWN', str(t_elapsed))
        else:
            message = get_msg_as_json('MAUKA', plugin, 'DOWN', 'NO_SHOW')
        save_message(message)

# NOTE - Must check overall status + individual plugin status
def check_mauka(config):
    sleep_time = config['interval']

    while True:
        try:
            with requests.Session() as req:
                response = req.get(config['url'])
            status = response.status_code
            if status == 200:
                message = get_msg_as_json('MAUKA', 'OVERALL', 'UP', status)
                mauka_plugins = response.json()
                check_mauka_plugins(config['plugins'], mauka_plugins)
            else:
                message = get_msg_as_json('MAUKA', 'OVERALL', 'DOWN', status)
        except Exception as e:
            message = get_msg_as_json('MAUKA', 'OVERALL', 'DOWN', e)
        save_message(message)
        sleep(10)

def main(config_file):
    health_config = file_to_dict(config_file)
    
    health_health_config = health_config[6]
    health_thread = Thread(target=check_health, args=(health_health_config, ))
    health_thread.start()

    view_config = health_config[4]
    view_thread = Thread(target=check_view, args=(view_config, ))
    view_thread.start()

    box_config = health_config[1]
    zmq_port = health_config[0]['port']
    box_thread = Thread(target=check_boxes, args=(box_config,zmq_port, ))
    box_thread.start()

    mongo_config = health_config[5]
    mongo_thread = Thread(target=check_mongo, args=(mongo_config, ))
    mongo_thread.start()

    mauka_config = health_config[2]
    mauka_thread = Thread(target=check_mauka, args=(mauka_config, ))
    mauka_thread.start()

    health_thread.join()
    view_thread.join()
    box_thread.join()
    mongo_thread.join()
    #mauka_thread.join()

def parse_cmd_args():
    parser = argparse.ArgumentParser(description='Get config and log file names')
    parser.add_argument('-config', nargs=1, help='Name of config file', default=['config.json'])
    parser.add_argument('-log', nargs=1, help='Name of log file', default=['log.txt'])
    args = parser.parse_args()
    return args.config[0], args.log[0]

def set_g_log_file(file_name):
    global g_log_file
    g_log_file = file_name

if __name__ == '__main__':
    # Use log_file as global variable
    config_file, log_file = parse_cmd_args()
    set_g_log_file(log_file)
    print('... reading configuration information from ' + config_file)
    print('... writing out health status to ' + log_file)
    main(config_file)
