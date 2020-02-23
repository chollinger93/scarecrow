import pytest
from scarecrow_core.plugins.audio import AudioPlugin
import configparser

def test_play_sound():
    # Read config
    conf = configparser.ConfigParser()
    conf.read('../resources/tests/plugins.d/audio.ini')
    a = AudioPlugin(conf)
    print('Playing sound')
    a.play_sound('../resources/tests/warning.mp3', streamer='pygame')

    with pytest.raises(NotImplementedError):
        a.play_sound('../resources/tests/warning.mp3', streamer='invalid')

    with pytest.raises(Exception):
        a.play_sound('../resources/tests/nofilehere.mp4', streamer='pygame')