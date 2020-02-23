import numpy as np
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
import multiprocessing
import cv2
from vidgear.gears import NetGear
from scarecrow_core.tensor_detectors.detector import run_inference_for_single_image, load_model, detect
from scarecrow_core.network.messages import Messages
from scarecrow_core.plugin_base.utils import *
import configparser
import argparse
import os

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()


def receive(category_index, model, address, port, protocol, pattern=0, min_detections=10, min_confidence=0.7,
            server_plugins={}, **kwargs):
    """Main receiver loop for network detection

    Args:
        category_index (category_index): category_index
        model (model): Model to use
        address (str): URL of `OpenCV` sender / Pi
        port (int): Port of `OpenCV` sender / Pi
        protocol (str): Protocol of of `OpenCV` sender / Pi
        pattern (int, optional): ZMQ Pattern. 0=`zmq.PAIR`, 1=`zmq.REQ/zmq.REP`; 2=`zmq.PUB,zmq.SUB`. Defaults to 0.
        min_detections (int, optional): Minimum detections required to yield a positive result. Defaults to 10.
        min_confidence (float, optional): Minimum average confidence required to yield a positive result. Defaults to 0.7.

    Yields:
        bool: True for a successful detection
    """
    client = NetGear(address=address, port=str(port), protocol=protocol,
                     pattern=pattern, receive_mode=True, logging=True)  # Define netgear client at Server IP address.

    # For detection thresholds
    c = 0
    if 'detection_threshold' in kwargs and 'fps' in kwargs:
        THRESHOLD_FRAMES = kwargs.get(
            'detection_threshold') * kwargs.get('fps')
        logger.debug('Using {} frames as {}s threshold'.format(
            THRESHOLD_FRAMES, kwargs.get('detection_threshold')))
    else:
        THRESHOLD_FRAMES = -1
        logger.warning('Threshold is disabled')

    # Detection
    i = 0
    confidence = 0
    p_res = False

    # infinite loop
    while True:
        # receive frames from network
        # TODO: time sleep comes from my fork of vidgear - might break lib
        frame = client.recv()
        logger.debug('Image received')
        image_np = np.copy(frame)
        # check if frame is None
        if image_np is None:
            logger.error('No frame available')
            break

        c += 1
        # If threshold is enabled, drop frames if we got a previous result and are below the detection threshold
        if THRESHOLD_FRAMES != -1 and c < THRESHOLD_FRAMES and p_res:
            logger.debug('Below threshold, dropping frame at {}'.format(c))
            continue

        # Server plugins - before
        run_image_detector_plugins_before(server_plugins, image_np)

        # Actual detection.
        res, i, confidence, np_det_img = detect(model, category_index, image_np,
                                                i, confidence,
                                                min_detections, min_confidence)                                     
        if res:
            yield True
            p_res = res   

        # Server plugins - after
        run_image_detector_plugins_after(
            server_plugins, res, i, confidence, np_det_img)

        key = cv2.waitKey(1) & 0xFF
        # check for 'q' key-press
        if key == ord("q"):
            # if 'q' key-pressed break out
            break

    # close output window
    cv2.destroyAllWindows()
    # safely close client
    client.close()

# use_sender_thread  # detection_threshold


def main(conf, conf_path, **kwargs):
    """Main function for receiver
    
    Args:
        conf (dict): Configuration file
        conf_path (str): Configuration path (plugins)
    
    Yields:
        bool: Detection successful
    """
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = '../models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS, use_display_name=True)

    detection_model = load_model(conf['Tensorflow']['ModelUrl'])

    # Client Plugins
    loaded_plugins = load_plugins(plugins=conf['Plugins']['Enabled'].split(
        ','), conf_path=conf_path+'plugins.d')

    # Start loop
    for res in receive(category_index,
                       detection_model,
                       conf['ZmqCamera']['IP'],
                       conf['ZmqCamera']['Port'],
                       conf['ZmqCamera']['Protocol'],
                       int(conf['ZmqCamera']['Pattern']),
                       float(conf['Detection']['min_detections']),
                       float(conf['Detection']['min_confidence']),
                       server_plugins=loaded_plugins,
                       **kwargs):
        logger.debug('Received signal')
        if kwargs.get('use_sender_thread', False):
            send_async_messages(loaded_plugins)
        else:
            send_messages(loaded_plugins)
        # For downstream
        yield res


if __name__ == "__main__":
    # Args
    parser = argparse.ArgumentParser(description='Runs local image detection')
    parser.add_argument('--config', '-c', dest='conf_path', type=str, required=False,
                        help='Path to config dir')
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf_path = args.conf_path

    if conf_path is None:
        conf_path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '../conf/')
        conf_path_core = '{}{}'.format(conf_path, 'config.ini')
        logger.warning('No conf path, using {}'.format(conf_path_core))
        conf.read(conf_path_core)
    else:
        #conf_path = '../conf'
        conf.read('{}/config.ini'.format(conf_path))

    # Main
    for res in main(conf,
                    conf_path=conf_path,
                    use_sender_thread=conf.getboolean(
                        'Plugins', 'UseSenderThread'),
                    detection_threshold=int(
                        conf['Detection']['DetectionStopThresholdSeconds']),
                    fps=int(
                        conf['Video']['FPS'])):
        pass
