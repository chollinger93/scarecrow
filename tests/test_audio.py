import pytest
from plugins.audio import AudioPlugin
import configparser

def test_play_sound():
    # Read config
    conf = configparser.ConfigParser()
    conf.read('tests/resources/plugins.d/audio.ini')
    a = AudioPlugin(conf)
    print('Playing sound')
    a.play_sound('tests/resources/warning.mp3', streamer='pygame')

    with pytest.raises(NotImplementedError):
        a.play_sound('tests/resources/warning.mp3', streamer='invalid')

    with pytest.raises(Exception):
        a.play_sound('tests/resources/nofilehere.mp4', streamer='pygame')