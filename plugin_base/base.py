import zmq


class ZmqBasePlugin:
    def __init__(self, configuration):
        self.configuration = configuration
        self.recv_server = configuration['ZmqReceiver']['IP']
        self.recv_port = configuration['ZmqReceiver']['Port']
        self.send_server = configuration['ZmqSender']['IP']
        self.send_port = configuration['ZmqSender']['Port']

    def on_receive(self, *args):
        print('on_receive is not implemented in {}'.format(
            self.__class__.__name__))
        pass

    def send_ack(self, socket, *args):
        print('send_ack is not implemented in {}'.format(self.__class__.__name__))
        #  Send acknowlede
        socket.send(b'Ack')

    def process(self, *args):
        print('process is not implemented in {}'.format(self.__class__.__name__))
        pass

    def start_receiver(self, *args):
        print('Starting receiver thread for ZMQ in {}...'.format(
            self.__class__.__name__))
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print('Binding to {}'.format(self.recv_server))
        socket.bind('tcp://*:{}'.format(self.recv_port))
        while True:
            #  Wait for next request from client
            message = socket.recv()
            self.on_receive(message)
            self.process(message)
            self.send_ack(socket)

    def start_sender(self, *args):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://{}:{}'.format(self.send_server, self.send_port))
        self.send(socket)
        self.on_ack(socket)

    def send(self, socket, *args):
        print('send is not implemented in {}'.format(self.__class__.__name__))
        msg = 'no_implemented'
        print('Sending message {} to server {}:{}'.format(msg, self.send_server, self.send_port))
        socket.send_string(msg)


    def on_ack(self, socket, *args):
        print('on_ack is not implemented in {}'.format(self.__class__.__name__))
        #  Send acknowlede
        #  Get the reply.
        response = socket.recv()
        print('Received response: {}'.format(response))

    
