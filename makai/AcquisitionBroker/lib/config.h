#ifndef ACQUISITION_BROKER_CONFIG_HPP
#define ACQUISITION_BROKER_CONFIG_HPP

#include <string>
#include <stdint.h>

using std::string;

//Redis keys for various data fields.

//sorted set of event numbers by timestamp
static const string EVENT_ZSET = "events.list";
//sorted set of event metadata by event number
static const string EVENT_META = "events.meta";
//Prefix for a box event data list. it is followed by "evenNum.Boxid"
static const string EVENT_BOX_DATA_PREFIX = "events";

//Configuration struct. All fields are loaded from json.
struct Config {
    Config(string fname = "/etc/opq/acquisition_broker_config.json");

    //folder with client public certificates.
    string public_certs;
    //Server private certificate
    string private_cert;
    //Box public interface for sending data requests
    string box_interface_pub;
    //Box public interface for receiving data replies.
    string box_interface_pull;
    //cloudside interfacce for receiving event requests
    string backend_interface_rep;
    //cloudside interfacce for receiving event numbers
    string backend_interface_pub;
    //hosname for redis server
    string redis_host;
    //portname for redis server
    int redis_port;
    //redis password
    string redis_pass;

};

#endif