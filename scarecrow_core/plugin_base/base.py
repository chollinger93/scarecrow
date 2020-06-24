import zmq

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

class BasePlugin:
    """Base plugin class
    """
    name = None

    def __init__(self, configuration):
        self.configuration = configuration
        logger.debug('Loaded plugin {}'.format(self.__class__.__name__))


class ImageDetectorBasePlugin(BasePlugin):
    """Server plugin that runs before and after the image detection
    """

    def __init__(self, configuration):
        self.configuration = configuration
        BasePlugin.__init__(self, configuration)

    def run_before(self, *args, **kwargs):
        logger.debug('run_before is not implemented in {}'.format(
            self.__class__.__name__))
        pass

    def run_after(self, *args, **kwargs):
        logger.debug('run_after is not implemented in {}'.format(
            self.__class__.__name__))
        pass


class ZmqBasePlugin(BasePlugin):
    """ZMQ Base plugin to implement sender/receiver plugins

    Runs on the client 
    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.recv_server = configuration['ZmqReceiver']['IP']
        self.recv_port = configuration['ZmqReceiver']['Port']
        self.send_server = configuration['ZmqSender']['IP']
        self.send_port = configuration['ZmqSender']['Port']
        BasePlugin.__init__(self, configuration)


    def on_receive(self, *args, **kwargs):
        """Called on receving a message
        """
        logger.debug('on_receive is not implemented in {}'.format(
            self.__class__.__name__))
        pass

    def send_ack(self, socket, *args, **kwargs):
        """Sends acknowledgement. Called after `process`

        Args:
            socket (socket): `ZMQ` socket
        """
        logger.debug('send_ack is not implemented in {}'.format(self.__class__.__name__))
        #  Send acknowlede
        socket.send(b'Ack')

    def process(self, *args, **kwargs):
        """Processes the message. Called after `on_receive`
        """
        logger.debug('process is not implemented in {}'.format(self.__class__.__name__))
        pass

    def start_receiver(self, *args, **kwargs):
        """Starts the main reciver loop
        """
        logger.debug('Starting receiver thread for ZMQ in {}...'.format(
            self.__class__.__name__))
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        logger.debug('Binding to {}'.format(self.send_server))
        socket.bind('tcp://*:{}'.format(self.send_port))
        while True:
            #  Wait for next request from client
            message = socket.recv()
            self.on_receive(message)
            self.process(message)
            self.send_ack(socket)

    def start_sender(self, *args, **kwargs):
        """Starts the main sender loop
        """
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://{}:{}'.format(self.recv_server, self.recv_port))
        self.send(socket)
        self.on_ack(socket)

    def send(self, socket, *args, **kwargs):
        """Sends a message

        Args:
            socket (socket): `ZMQ` socket
        """
        logger.debug('send is not implemented in {}'.format(self.__class__.__name__))
        msg = 'no_implemented'
        logger.debug('Sending message {} to server {}:{}'.format(
            msg, self.recv_server, self.recv_port))
        socket.send_string(msg)

    def on_ack(self, socket, *args, **kwargs):
        """Prases ack message. Called after `send`

        Args:
            socket (socket): `ZMQ` socket
        """
        logger.debug('on_ack is not implemented in {}'.format(self.__class__.__name__))
        #  Send acknowlede
        #  Get the reply.
        response = socket.recv()
        logger.debug('Received response: {}'.format(response))
