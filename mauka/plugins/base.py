import datetime
import json
import logging
import multiprocessing
import threading
import time
import os

import bson
import bson.objectid
import zmq

import mongo.mongo
import protobuf.opq_pb2 as opqpb

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)


def run_plugin(plugin_class, config):
    def _run_plugin():
        plugin_instance = plugin_class(config)
        plugin_instance._run()

    process = multiprocessing.Process(target=_run_plugin)
    process.start()


def protobuf_decode_measurement(encoded_measurement):
    trigger_message = opqpb.TriggerMessage()
    trigger_message.ParseFromString(encoded_measurement)
    return trigger_message


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class MaukaPlugin:
    def __init__(self, config, subscriptions, name):
        self.config = config
        self.subscriptions = subscriptions
        self.name = name

        self.mongo_client = self.get_mongo_client()

        self.zmq_context = zmq.Context()
        self.zmq_consumer = self.zmq_context.socket(zmq.SUB)
        self.zmq_consumer.connect(self.config_get("zmq.triggering.interface"))
        self.zmq_consumer.connect(self.config_get("zmq.mauka.sub.interface"))

        self.zmq_producer = self.zmq_context.socket(zmq.PUB)
        self.zmq_producer.connect(self.config_get("zmq.mauka.pub.interface"))

        # Statistics
        self.on_message_cnt = 0
        self.last_received = 0

    def get_status(self):
        return "N/A"

    def to_json(self, obj):
        return json.dumps(obj, cls=JSONEncoder)

    def from_json(self, json_str):
        return json.loads(json_str)

    def get_mongo_client(self):
        mongo_host = self.config_get("mongo.host")
        mongo_port = self.config_get("mongo.port")
        mongo_db = self.config_get("mongo.db")
        return mongo.mongo.OpqMongoClient(mongo_host, mongo_port, mongo_db)

    def start_heartbeat(self):
        def heartbeat():
            self.produce("heartbeat".encode(), "{}:{}:{}:{}".format(self.name, self.on_message_cnt, self.last_received, self.get_status()).encode())
            timer = threading.Timer(60.0, heartbeat)
            timer.start()

        threading.Timer(5.0, heartbeat).start()

    def config_get(self, key):
        if key not in self.config:
            raise KeyError("Key {} not in config".format(key))
        else:
            return self.config[key]

    def object_id(self, oid):
        return bson.objectid.ObjectId(oid)

    def on_message(self, topic, message):
        _logger.info("on_message not implemented")

    def produce(self, topic, message):
        self.zmq_producer.send_multipart((topic, message))

    def _run(self):
        for subscription in self.subscriptions:
            self.zmq_consumer.setsockopt_string(zmq.SUBSCRIBE, subscription)

        self.start_heartbeat()

        while True:
            data = self.zmq_consumer.recv_multipart()

            if len(data) != 2:
                _logger.error("Malformed data from ZMQ. Data size should = 2, but instead is {}".format(len(data)))
                break

            topic = data[0].decode()
            message = data[1]

            # Update statisics
            self.on_message_cnt += 1
            self.last_received = time.time()
            self.on_message(topic, message)

        _logger.info("Exiting Mauka plugin: {}".format(self.name))
