#include <iostream>
#include <memory>
#include <experimental/filesystem>
#include <MongoDriver.h>
#include "zmqpp/zmqpp.hpp"
#include "zmqpp/z85.hpp"
#include "DataHandler.h"
#include "RequestHandler.h"
#include "util.h"
#include <syslog.h>

using namespace std;

namespace fs = std::experimental::filesystem;


int main(int argc, char **argv) {
    setlogmask (LOG_UPTO (LOG_NOTICE));
    openlog ("AcquisitionBroker", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);
    syslog(LOG_NOTICE, "Parsing config.");
    Config config = argc == 1 ? Config{} : Config{argv[1]};
    //Load our certificate. Make sure we gor both public and private keys.

    auto server_cert = load_certificate(config.private_cert);
    syslog(LOG_NOTICE, ("server public key " +  server_cert.first).c_str());
    //Make sure that there is a certificate directory.
    fs::path client_certs(config.public_certs);

    if(!fs::is_directory(client_certs)){
        cout << "Could not load settings" << endl;
        syslog(LOG_ERR, "Could not load settings");
        return -1;
    }

    //Initialize mongo
    MongoDriver::init_mongo_client();

    //Create a zmq context and auth
    auto ctx = zmqpp::context();
    zmqpp::auth auth{ctx};
    auth.set_verbose(false);
    auth.configure_domain("*");

    int count = 0;
    //Load all of the client public keys.
    try {
        for (auto &cert_enrty: fs::recursive_directory_iterator(config.public_certs)) {
            auto client_public_cert = load_certificate(cert_enrty.path().string()).first;
            //configure auth to accept client
            auth.configure_curve(client_public_cert);
            count++;
        }
    }
    catch(runtime_error &e){
        cout << e.what() << endl;
        return -1;
    }
    syslog(LOG_NOTICE, ("Loaded " + std::to_string(count) + " keys").c_str());

    //Create a data handler object and
    DataHandler data_handler(config, ctx);
    //Create a new thread to handle data
    auto data_thread = thread([&data_handler](){data_handler.handle_data_loop();});

    //Create a request handler object
    RequestHandler request_handler(config, ctx);
    //Run the event loop.
    request_handler.handle_request_loop();
    closelog ();
    return 0;
}

