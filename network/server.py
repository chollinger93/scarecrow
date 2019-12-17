import time
import zmq

from . import messages
import multiprocessing as mp

import sys
sys.path.append('..')
from audio.player import play_sound

def receive_messages(server, port, streamer, audio_path, *args):
    print('Starting receiver thread for ZMQ...')
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:{}'.format(port))

    while True:
        #  Wait for next request from client
        message = socket.recv()
        print('Received request: {}'.format(message))
        print(str(messages.Messages.WARN.value))
        if message.decode('ascii') == str(messages.Messages.WARN.value):
            print('Playing warning')
            play_sound('{}/warning.mp3'.format(audio_path), streamer)
        elif message.decode('ascii') == str(messages.Messages.MUSIC.value):
            print('Playing Music')
            play_sound('{}/music.mp3'.format(audio_path), streamer) 
        else:
            print('Can\'t parse message!')

        #  Send acknowlede
        socket.send(b'Ack')

def start_zmq_thread(server, port, audio_path, streamer='pygame', msg=messages.Messages.WARN):
    # TODO: *args msg
    p = mp.Process(target=receive_messages, args=(server, port, streamer, audio_path, msg, ))
    # Set as daemon, so it gets killed alongside the parent
    p.daemon = True
    p.start()