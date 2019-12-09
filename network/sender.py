import zmq

def send_command(server, port, *args):
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(server, port))

    for msg in args:
        print('Sending message {} to server {}:{}'.format(msg, server, port))
        socket.send_string(str(msg.value))

        #  Get the reply.
        response = socket.recv()
        print('Received response: {}'.format(response))