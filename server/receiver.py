# import libraries
import sys
sys.path.append('..')
import configparser
from network.messages import Messages
from network.sender import send_command
from tensor_detectors.detector import run_inference_for_single_image, load_model
from vidgear.gears import NetGear
import cv2
import multiprocessing

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import numpy as np



def receive(category_index, model, address, port, protocol, min_detections=10, min_confidence=0.3):
    # define netgear client with `receive_mode = True` and default settings
    #client = NetGear(receive_mode=True)
    client = NetGear(address=address, port=str(port), protocol=protocol,
                     pattern=0, receive_mode=True, logging=True)  # Define netgear client at Server IP address.

    # For detection thresholds
    confidence = 0
    avg_confidence = 0
    i = 0
    # infinite loop
    while True: # TODO: FPS limit
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
        output_dict = run_inference_for_single_image(model, image_np)
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks_reframed', None),
            use_normalized_coordinates=True,
            line_thickness=8)

        cv2.imshow('object_detection', cv2.resize(image_np, (800, 600)))
        # print the most likely
        max_label = category_index[1]
        max_score = output_dict['detection_scores'][0]  # ['name']
        if max_label['name'] == 'person':
            i += 1
            confidence += max_score
            avg_confidence = confidence/i
        print('{} {}'.format(i, avg_confidence))
        if i >= min_detections and avg_confidence >= min_confidence:
            print('HUMAN DETECTED! DEPLOY BORK BORK NOM NOM! {} {}'.format(
                i, avg_confidence))
            i = 0
            avg_confidence = 0
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


def main(address, port, protocol, zmq_ip, zmq_port, min_detections, min_confidence):
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = '../models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS, use_display_name=True)

    model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
    detection_model = load_model(model_name)

    for res in receive(category_index, detection_model, address, port, protocol, min_detections, min_confidence):
        print('Received signal')
        send_command(zmq_ip, zmq_port, Messages.WARN)


if __name__ == "__main__":
    # Conf
    conf = configparser.ConfigParser()
    conf.read('../conf/config.ini')
    main(conf['Video']['IP'], conf['Video']['Port'], conf['Video']['Protocl'],
         conf['ZmqCamera']['IP'], conf['ZmqCamera']['Port'], 
         float(conf['Detection']['min_detections']), float(conf['Detection']['min_confidence']))
