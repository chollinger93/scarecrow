import time
import zmq
import multiprocessing as mp
import configparser
from scarecrow_core.plugins.audio import AudioPlugin
from scarecrow_core.plugins.store_video import StoreVideoPlugin
from scarecrow_core.plugins.motion import MotionDetectionPlugin
import inspect
from .interceptor import PluginInterceptor
from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

# Read config

def load_plugins(plugins, conf_path='../conf/plugins.d'):
    """Loads all plugins defined in `__allowed_plugins__`

    Args:
        plugins (list): Plugins to load
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
            raise NotImplementedError('Plugin {} not in allowed list: {}'.format(plugin, pi.allowed_plugins))
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
    if callback:
        callback()

def _run_image_detector_plugin(typ, loaded_plugins, mode, callback=None, callback_args=[], *args, **kwargs):
    _cargs = []
    logger.debug('Loaded Image Detectors in {}: '.format(mode) +str(loaded_plugins))
    if 'ImageDetectorBasePlugin' in loaded_plugins:
        for plugin in loaded_plugins['ImageDetectorBasePlugin']:
            logger.debug('run_image_detector_plugins_before mode: {} has {} ?= {}'.format(plugin.name, plugin.mode, mode))
            if plugin.mode == mode:
                if typ == 'before':
                    r = plugin.run_before(*args, **kwargs)
                else:
                    r = plugin.run_after(*args, **kwargs)
                logger.debug('Got args: {}'.format(r))
                if r:
                    _cargs.append(r)
    else:
        logger.warning('No ImageDetectorBasePlugins ({}) loaded'.format(mode))
    # Callback
    if callback:
        callback(*callback_args, *_cargs)

def run_image_detector_plugins_before(loaded_plugins, mode, callback, callback_args, *args, **kwargs):
    return _run_image_detector_plugin('before', loaded_plugins, mode, callback, callback_args, *args, **kwargs)

def run_image_detector_plugins_after(loaded_plugins, mode, callback, callback_args, *args, **kwargs):
    return _run_image_detector_plugin('after', loaded_plugins, mode, callback, callback_args, *args, **kwargs)

def load_image_detector_client_plugins(loaded_plugins):
    _cplugs = []
    if 'ImageDetectorBasePlugin' in loaded_plugins:
        for plugin in loaded_plugins['ImageDetectorBasePlugin']:
            _cplugs.append(plugin)
    return _cplugs