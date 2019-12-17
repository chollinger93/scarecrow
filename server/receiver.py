import sys
sys.path.append('..')

import numpy as np
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
import multiprocessing
import cv2
from vidgear.gears import NetGear
from tensor_detectors.detector import run_inference_for_single_image, load_model, detect
from network.sender import send_command, start_sender_thread
from network.messages import Messages
import configparser


def receive(category_index, model, address, port, protocol, min_detections=10, min_confidence=0.7):
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
        # print(image_np)
        print('Image received')
        image_np = np.copy(frame)
        # check if frame is None
        if image_np is None:
            # if True break the infinite loop
            break

        # Actual detection.
        res, i, confidence = detect(model, category_index, image_np,
                                    i, confidence,
                                    min_detections, min_confidence)
        if res:
            yield True

        key = cv2.waitKey(1) & 0xFF
        # check for 'q' key-press
        if key == ord("q"):
            # if 'q' key-pressed break out
            break

    # close output window
    cv2.destroyAllWindows()
    # safely close client
    client.close()


def main(address, port, protocol, zmq_ip, zmq_port, min_detections, min_confidence, model_name, use_sender_thread):
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = '../models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS, use_display_name=True)

    detection_model = load_model(model_name)

    for res in receive(category_index, detection_model, address, port, protocol, min_detections, min_confidence):
        print('Received signal')
        if use_sender_thread:
            start_sender_thread(zmq_ip, zmq_port, Messages.WARN)
        else:
            send_command(zmq_ip, zmq_port, Messages.WARN)


if __name__ == "__main__":
    # Conf
    conf = configparser.ConfigParser()
    conf.read('../conf/config.ini')
    main(conf['Video']['IP'], conf['Video']['Port'], conf['Video']['Protocl'],
         conf['ZmqCamera']['IP'], conf['ZmqCamera']['Port'],
         float(conf['Detection']['min_detections']), float(
             conf['Detection']['min_confidence']),
         model_name=conf['Tensorflow']['ModelUrl'],
         use_sender_thread=conf.getboolean('General', 'UseSenderThread'))
