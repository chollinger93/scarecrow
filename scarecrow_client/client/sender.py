# import libraries
from vidgear.gears import VideoGear
from vidgear.gears import NetGear
import numpy as np
from scarecrow_core.utilities.utils import *
from scarecrow_core.plugin_base.utils import *

import argparse
import configparser
import time

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

def _conditional_send(server, frame, client_plugins, *args):
    # if we have no plugins, don't bother being conditional
    _has_ret = False 
    
    for p in client_plugins:
        logger.debug('Plugin {} returns data? {}'.format(p.name, p.has_ret))
        if p.has_ret:
            _has_ret = True 
            break 
        
    if _has_ret and True in args:
        server.send(frame)
    else:
        #logger.debug('No ret client plugins, just sending at will')
        server.send(frame)

def run_camera(input_str, address, port, protocol, pattern=0, fps=25, client_plugins={}):
    """Runs the camera, sends messages

    Args:
        input_str (str): Path to video file **OR** an `int` for camera input
        address (str): URL of `OpenCV` server 
        port (int): Port of `OpenCV` server
        protocol (str): Protocol of of `OpenCV` server 
        pattern (int, optional): ZMQ Pattern. 0=`zmq.PAIR`, 1=`zmq.REQ/zmq.REP`; 2=`zmq.PUB,zmq.SUB`. Defaults to 0.
        fps (int, optional): Framerate for video capture. Defaults to 25.
    """
    if input_str.isdigit():
        input = int(input_str)
    else:
        input = input_str

    options = {'THREADED_QUEUE_MODE': False}
    if address == '':
        address = None
    # Open any video stream; `framerate` here is just for picamera
    stream = VideoGear(source=input, framerate=fps, **options).start()
    # server = NetGear() # Locally
    netgear_options = {'max_retries': 10, 'request_timeout': 10}
    server = NetGear(address=address, port=port, protocol=protocol,
                     pattern=pattern, receive_mode=False, logging=True, **netgear_options)

    # Plugin parsing
    c_plugs = load_image_detector_client_plugins(client_plugins)
    # infinite loop until [Ctrl+C] is pressed
    _prev_frame = None
    while True:
        # Sleep
        time.sleep(0.02)

        # Client plugins - before
        run_image_detector_plugins_before(client_plugins, 'client', None, None, _prev_frame)

        try:
            frame = stream.read()
            # check if frame is None
            if frame is None:
                logger.error('No frame available')
                break

            # Client plugins - after
            run_image_detector_plugins_after(client_plugins, 'client', 
                _conditional_send, [server, frame, c_plugs], np.copy(frame))
            _prev_frame = frame 

            # send frame to server
            # server.send(frame)

        except KeyboardInterrupt:
            # break the infinite loop
            break

    # safely close video stream
    stream.stop()

def start():
    """Setup.py entry point
    """
    # Args
    parser = argparse.ArgumentParser(description='Runs local image detection')
    parser.add_argument('--input', '-i', dest='in_file', type=str, required=True, default=0,
                        help='Input file (0 for webcam)')
    parser.add_argument('--config', '-c', dest='conf_path', type=str, required=True,
                        help='Path to config dir')
    import sys
    print(f'Args: {sys.argv}')
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf_path = args.conf_path

    # Read config
    conf_path = os.path.abspath(conf_path)
    logger.info('Reading config at {}'.format(conf_path))
    conf.read('{}/config.ini'.format(conf_path))

    # Plugin ZMQ threads
    _proc_plugs = load_plugins(
        conf['Plugins']['Enabled'].split(','), conf_path=conf_path+'/plugins.d')
    start_receiver_plugins(_proc_plugs)

    logger.info('Starting camera stream')
    run_camera(args.in_file, conf['ZmqServer']['IP'], conf['ZmqServer']['Port'], conf['ZmqServer']['Protocol'],
               int(conf['ZmqServer']['Pattern']), int(conf['Video']['FPS']), client_plugins=_proc_plugs)

if __name__ == "__main__":
    start()