import sys
sys.path.append('..')
from audio.player import *
import pytest

def test_play_sound():
    print('Playing sound')
    play_sound('./resources/warning.mp3', streamer='pygame')

    with pytest.raises(NotImplementedError):
        play_sound('./resources/warning.mp3', streamer='invalid')

    with pytest.raises(Exception):
        play_sound('./resources/nofilehere.mp4', streamer='pygame')