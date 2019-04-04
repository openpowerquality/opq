#include <string>
#include <stdint.h>

using std::string;

class Config{
	public:
	Config(string var_name = "TRIGGERING_BROKER_SETTINGS");
        string publicCerts(){return _public_certs;}
        string privateCert(){return _private_cert;}
        string boxPort() {return _box_interface;}
        string backendPort(){return _backend_interface;}
		bool whiteList(){return _white_list;}
	private:
		string _public_certs;
		string _private_cert;
        string _box_interface;
        string _backend_interface;
		bool _white_list;
};
