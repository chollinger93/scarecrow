# import libraries
from vidgear.gears import VideoGear
from vidgear.gears import NetGear

import sys
sys.path.append('..')
from utilities.utils import *
from network.server import start_zmq_thread

import argparse
import configparser
import time 
def run_camera(input_str, address, port, protocol, fps=25):
    """Runs the camera, sends messages
    
    Args:
        input_str (str): Path to video file **OR** an `int` for camera input
        address (str): URL of `OpenCV` server 
        port (int): Port of `OpenCV` server
        protocol (str): Protocol of of `OpenCV` server 
        fps (int, optional): Framerate for video capture. Defaults to 25.
    """
    if input_str.isdigit():
        input = int(input_str)
    else: input = input_str

    # Open any video stream; `framerate` here is just for picamera
    stream = VideoGear(source=input, framerate=fps).start()
    # server = NetGear() # Locally
    server = NetGear(address=address, port=port, protocol=protocol,
                    pattern=0, receive_mode=False, logging=True) 

    # infinite loop until [Ctrl+C] is pressed
    while True:
        try:
            frame = stream.read()
            # check if frame is None
            if frame is None:
                print('No frame available')
                break

            # send frame to server
            server.send(frame)

        except KeyboardInterrupt:
            # break the infinite loop
            break

    # safely close video stream
    stream.stop()


if __name__ == "__main__":
    # Args
    parser = argparse.ArgumentParser(description='Runs local image detection')
    parser.add_argument('--input', '--i', dest='in_file', type=str, required=True, default=0,
                    help='Input file (0 for webcam)')
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf.read('../conf/config.ini')

    # Audio ZMQ thread
    start_zmq_thread(conf['ZmqServer']['IP'], conf['ZmqServer']['Port'], conf['Audio']['Path'], conf['Audio']['Streamer'])

    print('Starting camera stream')
    run_camera(args.in_file, conf['Video']['IP'], conf['Video']['Port'], conf['Video']['Protocol'], int(conf['Video']['FPS']))