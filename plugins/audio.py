import sys
sys.path.append('..')
from network.messages import Messages
from audio.player import play_sound
from plugin_base.base import *

class AudioPlugin(ZmqBasePlugin):
    def __init__(self, configuration):
        print(configuration['Audio'])
        self.audio_path = configuration['Audio']['Path']
        self.streamer = configuration['Audio']['Streamer']
        ZmqBasePlugin.__init__(self, configuration)

    def process(self, msg):
        if msg.decode('ascii') == str(Messages.WARN.value):
            print('Playing warning')
            play_sound('{}/warning.mp3'.format(self.audio_path), self.streamer)
        elif msg.decode('ascii') == str(Messages.MUSIC.value):
            print('Playing Music')
            play_sound('{}/music.mp3'.format(self.audio_path), self.streamer)
        else:
            print('Can\'t parse message!')

    def send_ack(self, socket, *args):
        #  Send acknowlede
        socket.send(b'Ack')

    def send(self, socket, *args):
        msg = Messages.WARN
        socket.send_string(str(msg.value))