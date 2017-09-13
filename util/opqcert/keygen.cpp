#include <czmq.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <string>
#include <iostream>
using namespace std;

void usage(){
	cout << "keygen dir name" << endl;
}

int main(int argc, char** argv){
	if(argc != 3){	
		usage();
		return -1;
	}
	struct stat st = {0};
	if (stat(argv[1], &st) == -1) {
		usage();
		return -1;		
	}
	string path = argv[1];
	path += "/";
	path += argv[2];
	zcert_t *server_cert = zcert_new ();
	zcert_save(server_cert, path.c_str());
	zcert_save_public(server_cert, path.c_str());

}
