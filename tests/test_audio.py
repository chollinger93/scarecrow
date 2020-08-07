import pytest
from scarecrow_core.plugins.audio import AudioPlugin
import configparser

RESOURCE_PATH='./resources'

def _check_skip_apt():
    try:
        import apt
        cache = apt.Cache()
        if cache['pygame'].is_installed:
            return False 
    except Exception as err:
        print('Cannot check pygame installation: {}'.format(err))
    return True 

@pytest.mark.skipif(_check_skip_apt(), reason='Cannot check pygame installation')
def test_play_sound():
    # Read config
    conf = configparser.ConfigParser()
    conf.read(RESOURCE_PATH+'/tests/plugins.d/audio.ini')
    a = AudioPlugin(conf)
    print('Playing sound')
    a.play_sound(RESOURCE_PATH+'/tests/warning.mp3', streamer='pygame')

    with pytest.raises(NotImplementedError):
        a.play_sound(RESOURCE_PATH+'/tests/warning.mp3', streamer='invalid')

    with pytest.raises(Exception):
        a.play_sound(RESOURCE_PATH+'/tests/nofilehere.mp4', streamer='pygame')