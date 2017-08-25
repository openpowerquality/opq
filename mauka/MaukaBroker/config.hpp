#include <string>
#include <stdint.h>

using std::string;

class Config{
	public:
		Config(string fname = "/etc/opq/opqmauka.broker.config.json");
        string boxPort() {return _box_interface;}
        string backendPort(){return _backend_interface;}
	private:
		string _public_certs;
		string _private_cert;
        string _box_interface;
        string _backend_interface;
};
