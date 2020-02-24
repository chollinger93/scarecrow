# import libraries
from vidgear.gears import VideoGear
from vidgear.gears import NetGear

from scarecrow_core.utilities.utils import *
from scarecrow_core.plugin_base.utils import *

import argparse
import configparser
import time

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()


def run_camera(input_str, address, port, protocol, pattern=0, fps=25):
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

    # Open any video stream; `framerate` here is just for picamera
    stream = VideoGear(source=input, framerate=fps).start()
    # server = NetGear() # Locally
    server = NetGear(address=address, port=port, protocol=protocol,
                     pattern=pattern, receive_mode=False, logging=True)

    # infinite loop until [Ctrl+C] is pressed
    while True:
        # Sleep
        time.sleep(0.02)

        try:
            frame = stream.read()
            # check if frame is None
            if frame is None:
                logger.error('No frame available')
                break

            # send frame to server
            server.send(frame)

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
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf_path = args.conf_path

    # Read config
    conf_path = os.path.abspath(conf_path)
    logger.info('Reading config at {}'.format(conf_path))
    conf.read('{}/config.ini'.format(conf_path))

    # Plugin ZMQ threads
    start_receiver_plugins(load_plugins(
        conf['Plugins']['Enabled'].split(','), conf_path=conf_path+'/plugins.d'))

    logger.info('Starting camera stream')
    run_camera(args.in_file, conf['ZmqServer']['IP'], conf['ZmqServer']['Port'], conf['ZmqServer']['Protocol'],
               int(conf['ZmqServer']['Pattern']), int(conf['Video']['FPS']))

if __name__ == "__main__":
    start()