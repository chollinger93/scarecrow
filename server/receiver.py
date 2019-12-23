import numpy as np
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
import multiprocessing
import cv2
from vidgear.gears import NetGear
from tensor_detectors.detector import run_inference_for_single_image, load_model, detect
from network.messages import Messages
from plugin_base.utils import *
import configparser
import argparse
import os 

from utilities.utils import get_logger
logger = get_logger()

def receive(category_index, model, address, port, protocol, min_detections=10, min_confidence=0.7, server_plugins={}):
    """Main receiver loop for network detection
    
    Args:
        category_index (category_index): category_index
        model (model): Model to use
        address (str): URL of `OpenCV` sender / Pi
        port (int): Port of `OpenCV` sender / Pi
        protocol (str): Protocol of of `OpenCV` sender / Pi
        min_detections (int, optional): Minimum detections required to yield a positive result. Defaults to 10.
        min_confidence (float, optional): Minimum average confidence required to yield a positive result. Defaults to 0.7.
    
    Yields:
        bool: True for a successful detection
    """
    client = NetGear(address=address, port=str(port), protocol=protocol,
                     pattern=0, receive_mode=True, logging=True)  # Define netgear client at Server IP address.

    # For detection thresholds
    confidence = 0
    i = 0
    # infinite loop
    while True:  # TODO: FPS limit
        # receive frames from network
        frame = client.recv()
        logger.debug('Image received')
        image_np = np.copy(frame)
        # check if frame is None
        if image_np is None:
            # if True break the infinite loop
            break

        # Server plugins - before
        run_image_detector_plugins_before(server_plugins, image_np)

        # Actual detection.
        res, i, confidence, np_det_img = detect(model, category_index, image_np,
                                    i, confidence,
                                    min_detections, min_confidence)
        if res:
            yield True

        # Server plugins - after
        run_image_detector_plugins_after(server_plugins, res, i, confidence, np_det_img)

        key = cv2.waitKey(1) & 0xFF
        # check for 'q' key-press
        if key == ord("q"):
            # if 'q' key-pressed break out
            break

    # close output window
    cv2.destroyAllWindows()
    # safely close client
    client.close()


def main(zmq_ip, zmq_port, zmq_protocol, min_detections, min_confidence, model_name, use_sender_thread, plugins, conf_path):
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = '../models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS, use_display_name=True)

    detection_model = load_model(model_name)

    # Client Plugins
    loaded_plugins = load_plugins(plugins=plugins, conf_path=conf_path+'plugins.d')
    for res in receive(category_index, detection_model, zmq_ip, zmq_port, zmq_protocol, min_detections, min_confidence, loaded_plugins):
        logger.debug('Received signal')
        if use_sender_thread:
            send_async_messages(loaded_plugins)
        else:
            send_messages(loaded_plugins)
        # For downstream
        yield res 


if __name__ == "__main__":
    # Args
    parser = argparse.ArgumentParser(description='Runs local image detection')
    parser.add_argument('--config', '-c', dest='conf_path', type=str, required=False, default='../conf',
                    help='Path to config dir')
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf_path = args.conf_path
    if conf_path is None:
        conf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../conf/')
        conf_path_core = '{}{}'.format(conf_path, 'config.ini')
        logger.warning('No conf path, using {}'.format(conf_path_core))
        conf.read(conf_path_core)
    else:
        conf.read('{}/config.ini'.format(conf_path))

    for res in main(conf['ZmqServer']['IP'], 
        conf['ZmqServer']['Port'],
        conf['ZmqServer']['Protocol'],
        float(conf['Detection']['min_detections']), 
        float(conf['Detection']['min_confidence']),
        model_name=conf['Tensorflow']['ModelUrl'],
        use_sender_thread=conf.getboolean('Plugins', 'UseSenderThread'),
        plugins=conf['Plugins']['Enabled'].split(','),
        conf_path=conf_path):
            pass
