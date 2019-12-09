import sys
sys.path.append('..')
from audio.player import *

def test_play_sound():
    print('Playing sound')
    play_sound('../audio_files/warning.mp3')