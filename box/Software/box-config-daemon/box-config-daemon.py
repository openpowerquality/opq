import http_server
import logging

# import pify.pify
# import pify.nmoperations

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usasge: ./box-config-daemon.py config_file server_port")
        exit(1)

    # logging.info("Starting PiFy FSM")
    # nm = pify.nmoperations.NM()
    # fsm_thread = pify.pify.PifyFsmThread(nm)
    # fsm_thread.start()


    config_file = sys.argv[1]
    port = int(sys.argv[2])

    http_server.run_server(port, config_file)
