import zmq
import multiprocessing as mp
from . import messages


def send_command(server, port, *args):
    """Sends a command via `ZMQ`
    
    Args:
        server (str): Server address
        port (int): Server port
    """
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(server, port))

    for msg in args:
        print('Sending message {} to server {}:{}'.format(msg, server, port))
        socket.send_string(str(msg.value))

        #  Get the reply.
        response = socket.recv()
        print('Received response: {}'.format(response))


def start_sender_thread(server, port, msg=messages.Messages.WARN):
    """Starts a sender thread for non-blocking network I/O
    
    Args:
        server (str): Server address
        port (int): Server port
        msg (messages.Messages, optional): Message type. Defaults to messages.Messages.WARN.
    
    Returns:
        Process: Process
    """
    # TODO: *args msg
    print('Starting sender thread')
    p = mp.Process(target=send_command, args=(server, port, msg, ))
    # Set as daemon, so it gets killed alongside the parent
    p.daemon = True
    p.start()
    return p
