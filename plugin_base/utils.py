import time
import zmq
import multiprocessing as mp
import configparser
from plugins.audio import AudioPlugin
from plugins.store_video import StoreVideoPlugin
import inspect
from plugin_base.interceptor import PluginInterceptor
from utilities.utils import get_logger
logger = get_logger()

# Read config

def load_plugins(plugins, conf_path='../conf/plugins.d'):
    """Loads all plugins defined in `__allowed_plugins__`

    Args:
        conf_path (str): Configuration path
    
    Raises:
        NotImplementedError: If an invalid plugin was specified
    
    Returns:
        dict: loaded_plugins
    """
    # Load plugins
    pi = PluginInterceptor()
    loaded_plugins = {}
    for plugin in plugins:
        # Read config
        conf = configparser.ConfigParser()
        logger.debug('Reading plugin config {}/{}.ini'.format(conf_path, plugin))
        conf.read('{}/{}.ini'.format(conf_path, plugin))
        # Check exists
        if plugin is None or plugin == '':
            continue
        # Check enabled
        if plugin not in pi.allowed_plugins:
            raise NotImplementedError
        else:
            # TODO: enable port conflict scan
            p = pi.allowed_plugins[plugin]
            o = p(conf)
            base = inspect.getmro(p)[1]
            if base.__name__ not in loaded_plugins:
                loaded_plugins[base.__name__] = []
            loaded_plugins[base.__name__].append(o)
    return loaded_plugins


def start_receiver_plugins(loaded_plugins):
    """Starts the daemon threads for the receiver plugins
    
    Args:
        loaded_plugins (dict): loaded_plugins
    
    Returns:
        list: Started processes
    """
    # Execution
    procs = []
    if 'ZmqBasePlugin' in loaded_plugins:
        for plugin in loaded_plugins['ZmqBasePlugin']:
            p = mp.Process(target=plugin.start_receiver)
            # Set as daemon, so it gets killed alongside the parent
            p.daemon = True
            p.start()
            procs.append(p)
    else:
        logger.warning('No ZmqBasePlugins loaded')
    return procs

def send_messages(loaded_plugins):
    """Sends a message across all plugins
    
    Args:
        loaded_plugins (list): loaded_plugins
    """
    if 'ZmqBasePlugin' in loaded_plugins:
        for se in loaded_plugins['ZmqBasePlugin']:
            se.start_sender()
    else:
        logger.warning('No ZmqBasePlugins loaded')

def send_async_messages(loaded_plugins):
    """Starts a separate thread to send all messages
    
    Args:
        loaded_plugins (list): loaded_plugins
    """
    if 'ZmqBasePlugin' in loaded_plugins:
        for se in loaded_plugins['ZmqBasePlugin']:
            p = mp.Process(target=se.start_sender)
            # Set as daemon, so it gets killed alongside the parent
            p.daemon = True
            p.start()
    else:
        logger.warning('No ZmqBasePlugins loaded')

def run_image_detector_plugins_before(loaded_plugins, *args, **kwargs):
    if 'ImageDetectorBasePlugin' in loaded_plugins:
        for plugin in loaded_plugins['ImageDetectorBasePlugin']:
            plugin.run_before(*args, **kwargs)
    else:
        logger.warning('No ImageDetectorBasePlugins loaded')

def run_image_detector_plugins_after(loaded_plugins, *args, **kwargs):
    if 'ImageDetectorBasePlugin' in loaded_plugins:
        for plugin in loaded_plugins['ImageDetectorBasePlugin']:
            plugin.run_after(*args, **kwargs)
    else:
        logger.warning('No ImageDetectorBasePlugins loaded')