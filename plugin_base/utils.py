import sys
sys.path.append('..')
import time
import zmq
import multiprocessing as mp
import configparser
from plugins.audio import AudioPlugin

# TODO: this should be a dynamic loader
__allowed_plugins__ = {
    'audio': AudioPlugin
}
plugins = ['audio']

def load_plugins():
    # Load plugins
    loaded_plugins = []
    for plugin in plugins:
        # Read config
        conf = configparser.ConfigParser()
        conf.read('../conf/plugins.d/{}.ini'.format(plugin))
        # Check enabled
        if plugin not in __allowed_plugins__:
            raise NotImplementedError
        else:
            # TODO: enable port conflict scan
            p = __allowed_plugins__[plugin](conf)
            loaded_plugins.append(p)
    return loaded_plugins


def start_receiver_plugins(loaded_plugins):
    # Execution
    procs = []
    for plugin in loaded_plugins:
        p = mp.Process(target=plugin.start_receiver)
        # Set as daemon, so it gets killed alongside the parent
        p.daemon = False
        p.start()
        procs.append(p)
    return procs

def send_messages(loaded_plugins):
    for se in loaded_plugins:
        se.start_sender()