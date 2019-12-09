# import libraries
from vidgear.gears import VideoGear
from vidgear.gears import NetGear

import sys
sys.path.append('..')
from utilities.utils import *
from network.server import start_zmq_thread

import argparse
import configparser

def run_camera(input_str, address, port, protocol):
    if input_str.isdigit():
        input = int(input_str)
    else: input = input_str

    # Open any video stream
    stream = VideoGear(source=input).start()
    # server = NetGear() # Locally
    server = NetGear(address=address, port=port, protocol=protocol,
                    pattern=0, receive_mode=False, logging=True) 

    # infinite loop until [Ctrl+C] is pressed
    while True:
        try:
            frame = stream.read()
            # read frames

            # check if frame is None
            if frame is None:
                # if True break the infinite loop
                break

            # do something with frame here

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
    run_camera(args.in_file, conf['Video']['IP'], conf['Video']['Port'], conf['Video']['Protocl'])