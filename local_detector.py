import sys
sys.path.append('./models/research/object_detection')
sys.path.append('./tensor_detectors')
from network.messages import Messages
from tensor_detectors.detector import load_model, label_map_util, run_inference
import configparser
import argparse
import cv2


if __name__ == "__main__":
    # Args
    parser = argparse.ArgumentParser(description='Runs local image detection')
    parser.add_argument('--input', '--i', dest='in_file', type=str, required=True,
                        help='Input file (0 for webcam)')
    args = parser.parse_args()
    # Conf
    conf = configparser.ConfigParser()
    conf.read('./conf/config.ini')

    print('Starting detection')
    # Define the video stream
    if args.in_file.isdigit():
        input = int(args.in_file)
    else:
        input = args.in_file

    # Capture locally
    print('Using input {}'.format(input))
    cap = cv2.VideoCapture(input)

    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = 'models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS, use_display_name=True)

    #model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
    model_name = conf['Tensorflow']['ModelUrl']
    detection_model = load_model(model_name)

    for res in run_inference(detection_model, cap, category_index,
                             float(conf['Detection']['min_detections']), float(
                                 conf['Detection']['min_confidence']),
                             fps=int(conf['Video']['FPS'])):
        print('Received signal')
