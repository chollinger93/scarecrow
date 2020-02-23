from scarecrow_core.network.messages import Messages
from scarecrow_core.plugin_base.base import *

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

class AudioPlugin(ZmqBasePlugin):
    name = 'audio'
    
    def __init__(self, configuration):
        self.audio_path = configuration['Audio']['Path']
        self.streamer = configuration['Audio']['Streamer']
        ZmqBasePlugin.__init__(self, configuration)

    def process(self, msg):
        if msg.decode('ascii') == str(Messages.WARN.value):
            logger.debug('Playing warning')
            self.play_sound('{}/warning.mp3'.format(self.audio_path), self.streamer)
        elif msg.decode('ascii') == str(Messages.MUSIC.value):
            logger.debug('Playing Music')
            self.play_sound('{}/music.mp3'.format(self.audio_path), self.streamer)
        else:
            logger.debug('Can\'t parse message!')

    def send_ack(self, socket, *args):
        #  Send acknowlede
        socket.send(b'Ack')

    def send(self, socket, *args):
        msg = Messages.WARN
        socket.send_string(str(msg.value))

    def play_sound(self, input, streamer='pygame'):
        """Plays a sound
        
        Args:
            input (str): Input file
            streamer (str, optional): Streamer to use to play audio. Defaults to 'pygame'.
        
        Raises:
            NotImplementedError: `streamer` not defined
        """
        logger.warning('Playing sound {}'.format(input))
        if streamer == 'pygame':
            from pygame import mixer
            mixer.pre_init(44100, -16, 1, 512)
            mixer.init()
            mixer.music.load(input)
            mixer.music.play()
            while mixer.music.get_busy() == True:
                continue
        elif streamer == 'playsound': 
            from playsound import playsound
            playsound(input)
        elif streamer == 'os':
            import subprocess
            subprocess.call(['omxplayer', input])
        elif streamer == 'none':
            return 
        else:
            raise NotImplementedError