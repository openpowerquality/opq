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
g_log_file_on = True
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
    write_to_log(get_log_msg(message))
    write_to_mongo(message)

def get_log_msg(message):
    serv = 'service: ' + message['service']
    id = 'service id: ' + str(message['serviceID'])
    stat = 'status: ' + message['status']
    info = 'info: ' + message['info']

    return ' '.join([ctime(), serv, id, stat, info])

def write_to_log(log_msg):
    global g_log_file_on
    if not g_log_file_on:
        return

    try:
        with open(g_log_file, 'a') as log_file:
            log_file.write(log_msg + '\n')
    except:
        print('Unable to write to ' + g_log_file)
        exit()

# NOTE - What if mongo is down?
# WIP - Add mongo uri?
def write_to_mongo(message):
    client = MongoClient()
    db = client['opq']
    coll = db['health']
  
    message['timestamp'] = datetime.utcnow()
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

def get_mongo_doc(uri, coll, doc):
    client = MongoClient(uri)
    db = client['opq']
    coll = db[coll]
    
    match = coll.find_one(doc)

    client.close()

    return match

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
            if time_elapsed > 20:
                message = get_msg_as_json('BOX', str(id), 'DOWN', '')
            else:
                message = get_msg_as_json('BOX', str(id), 'UP', '')
            save_message(message)
        lock.release()

def get_box_ids():
    # Pass mongo uri eventually
    client = MongoClient()
    db = client['opq']
    coll = db['opq_boxes']

    boxes = coll.find({}, {'_id': 0, 'box_id': 1})

    ids = [int(box['box_id']) for box in boxes]

    return ids

def check_boxes(config):
    sleep_time = config['interval']
    port = config['box_port']

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.connect(port)

    for id in get_box_ids():
        # Add each box id as a new key
        boxes[id] = 0

    box_log_thread = Thread(target=log_boxes, args=(sleep_time, ))
    box_log_thread.start()

    while True:
        # WIP - Add try/catch on recv?
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
        # Use health collection to check if up
        doc = get_mongo_doc(mongo_uri, 'health', {})
        if doc:
            message = get_msg_as_json('MONGO', '', 'UP', '')
        else:
            message = get_msg_as_json('MONGO', '', 'DOWN', '')
        save_message(message)
        sleep(sleep_time)

def check_mauka_plugins(config_plugins, mauka_plugins):
    plugins_up = True
    for plugin in config_plugins:
        if plugin in mauka_plugins:
            t_elapsed = time() - mauka_plugins[plugin]
            if t_elapsed >= 300:
                plugins_up = False
                break
        else:
            plugins_up = False
            break
    if plugins_up:
        message = get_msg_as_json('MAUKA', '', 'UP', '')
    else:
        message= get_msg_as_json('MAUKA', '', 'DOWN', '')
    save_message(message)

def check_mauka(config):
    sleep_time = config['interval']

    while True:
        try:
            with requests.Session() as req:
                response = req.get(config['url'])
            status = response.status_code
            if status == 200:
                mauka_plugins = response.json()
                check_mauka_plugins(config['plugins'], mauka_plugins)
            else:
                message = get_msg_as_json('MAUKA', '', 'DOWN', status)
                save_message(message)
        except Exception as e:
            message = get_msg_as_json('MAUKA', '', 'DOWN', e)
            save_message(message)
        sleep(sleep_time)

def generate_req_event_message():
    current_t_ms = int(time() * 1000)
    req_message = protobuf.opq_pb2.RequestEventMessage()

    req_message.trigger_type = req_message.OTHER
    req_message.description = "Health check"
    req_message.end_timestamp_ms_utc = int(current_t_ms - 10000)
    req_message.start_timestamp_ms_utc = int(current_t_ms - 20000)
    req_message.percent_magnitude = 50
    req_message.requestee = "Evan"
    req_message.request_data = False
    
    return req_message

def find_event(mongo_uri, new_event):
    if not new_event:
        return None
    # NOTE - Should I sleep for a bit to give event creation slack?
    id = int(new_event[1])
    event = get_mongo_doc(mongo_uri, 'events', {'event_id': id})

    return event

def check_makai(config):
    sleep_time = config['interval']
    push_port = config['push_port']
    sub_port = config['sub_port']
    mongo_uri = config['mongo']

    context = zmq.Context()

    push_socket = context.socket(zmq.PUSH)

    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
    # Timeout is 3 seconds for response
    sub_socket.rcvtimeo = 3000

    try:
        push_socket.connect(push_port)
        sub_socket.connect(sub_port)
    except Exception as e:
        message = get_msg_as_json('MAKAI', '', 'DOWN', e)
        save_message(message)
        exit()

    client = MongoClient()
    while True:
        req_message = generate_req_event_message()
        try:
            push_socket.send(req_message.SerializeToString())
            # receive any event id
            new_event = sub_socket.recv_multipart()
        except Exception as e:
            message = get_msg_as_json('MAKAI', '', 'DOWN', e)
            save_message(message)
            sleep(sleep_time)
            continue

        event = find_event(mongo_uri, new_event)
        if event:
            # Delete event
            db = client["opq"]
            events_collection = db["events"]
            box_events_collection = db["box_events"]
            event_id = event["event_id"]

            events_collection.delete_many({"event_id": event_id})
            box_events_collection.delete_many({"event_id": event_id})

            message = get_msg_as_json('MAKAI', '', 'UP', '')
        else:
            message = get_msg_as_json('MAKAI', '', 'DOWN', '')

        save_message(message)
        
        sleep(sleep_time)

    push_socket.close()
    sub_socket.clse()
           
def main(config_file):
    health_config = file_to_dict(config_file)

    health_health_config = health_config[5]
    health_thread = Thread(target=check_health, args=(health_health_config, ))
    health_thread.start()

    view_config = health_config[3]
    view_thread = Thread(target=check_view, args=(view_config, ))
    view_thread.start()

    box_config = health_config[0]
    box_thread = Thread(target=check_boxes, args=(box_config, ))
    box_thread.start()

    mongo_config = health_config[4]
    mongo_thread = Thread(target=check_mongo, args=(mongo_config, ))
    mongo_thread.start()

    mauka_config = health_config[1]
    mauka_thread = Thread(target=check_mauka, args=(mauka_config, ))
    mauka_thread.start()

    makai_config = health_config[2]
    makai_thread = Thread(target=check_makai, args=(makai_config, ))
    makai_thread.start()

    health_thread.join()
    view_thread.join()
    box_thread.join()
    mongo_thread.join()
    mauka_thread.join()
    makai_thread.join()

def parse_cmd_args():
    parser = argparse.ArgumentParser(description='Get config and log file names')
    parser.add_argument('-config', nargs=1, help='Name of config file', default=['config.json'])
    parser.add_argument('-log', nargs=1, help='Name of log file', default=['logfile.txt'])
    args = parser.parse_args()
    return args.config[0], args.log[0]

def set_g_log_file(file_name):
    global g_log_file
    global g_log_file_on

    g_log_file = file_name
    
    if g_log_file == 'disable':
        g_log_file_on = False
        
if __name__ == '__main__':
    # Use log_file as global variable
    config_file, log_file = parse_cmd_args()
    set_g_log_file(log_file)

    print('... reading configuration information from ' + config_file)

    if log_file != 'disable':
        print('... writing out health status to ' + log_file)
    else:
        print('... log file disabled')

    main(config_file)
