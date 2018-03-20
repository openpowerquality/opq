import zmq

def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:9881")
    socket.setsockopt(zmq.SUBSCRIBE, '')

    while True:
        measurement = socket.recv_string()
        print(message)

if __name__ == '__main__':
    main()
