import cv2
import pathlib
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops
from PIL import Image
from matplotlib import pyplot as plt
from io import StringIO
from collections import defaultdict
import zipfile
import tensorflow as tf
import tarfile
import six.moves.urllib as urllib
import os
import numpy as np
from audio import player
import time
import sys
sys.path.append('../models/research/object_detection')


def load_model(model_name):
    """Downloads a model from `download.tensorflow.org`
    
    Args:
        model_name (str): Model name
    
    Returns:
        model: Downloaded model
    """
    base_url = 'http://download.tensorflow.org/models/object_detection/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(
        fname=model_name,
        origin=base_url + model_file,
        untar=True)

    model_dir = pathlib.Path(model_dir)/"saved_model"
    print('Saved to {}'.format(model_dir))

    model = tf.saved_model.load(str(model_dir))
    model = model.signatures['serving_default']

    return model


def run_inference_for_single_image(model, image):
    """Runs detection on a single image
    
    Args:
        model (model): Model
        image (byte): Numpy image array
    
    Returns:
        dict: output_dict with labels/confidence
    """
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(
        np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(
            detection_masks_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def detect(model, category_index, image_np, i, confidence, min_detections=10, min_confidence=0.7):
    """Detection loop main method

    Runs actual detection
    
    Args:
        model (model): Model to use
        category_index (category_index): category_index
        image (byte): Numpy image array
        i (int): Iterator
        confidence (float): Previous confidence
        min_detections (int, optional): Minimum detections required to yield a positive result. Defaults to 10.
        min_confidence (float, optional): Minimum average confidence required to yield a positive result. Defaults to 0.7.
    
    Returns:
        (bool, int, float): Tuple with detection threshold, iterator, confidence
    """
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
    if 'detection_scores' not in output_dict or len(category_index) < 1 or len(output_dict['detection_scores']) <= 0:
        return (False, i, confidence)
    max_label = category_index[1]
    max_score = output_dict['detection_scores'][0]  # ['name']
    if max_label['name'] == 'person':
        i += 1
        confidence += max_score
        avg_confidence = confidence/i
    print('Count: {}, avg_confidence: {}'.format(i, avg_confidence))
    if i >= min_detections and avg_confidence >= min_confidence:
        print('HUMAN DETECTED! DEPLOY BORK BORK NOM NOM! {} {}'.format(
            i, avg_confidence))
        i = 0
        confidence = 0
        avg_confidence = 0
        return (True, i, confidence)
    else:
        return (False, i, confidence)


def run_inference(model, cap, category_index, min_detections=10, min_confidence=0.7, fps=25):
    """Runs a local detection loop, based on the `OpenCV` cap
    
    Args:
        model (model): Model to use
        cap (cap): `OpenCV` cap
        category_index (category_index): category_index
        min_detections (int, optional): Minimum detections required to yield a positive result. Defaults to 10.
        min_confidence (float, optional): Minimum average confidence required to yield a positive result. Defaults to 0.7.
        fps (int, optional): Framerate for video capture. Defaults to 25.
    """
    confidence = 0
    i = 0
    # FPS limiter - only for video streams
    print('Changing framerate from {} to {}'.format(cap.get(cv2.CAP_PROP_FPS), fps))
    #cap.set(cv2.CAP_PROP_FPS, fps)
    while(cap.isOpened()):
        ret, image_np = cap.read()
        print('Ret: {}'.format(ret))
        
        if image_np is None:
            print('Image is none')
            break

        # FPS limit
        cv2.waitKey(int( (1 / int(fps)) * 1000))

        # Actual detection.
        res, i, confidence = detect(model, category_index, image_np,
                                    i, confidence,
                                    min_detections, min_confidence)
        if res:
            print('Detected')
            yield True

        # check for 'q' key-press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            # if 'q' key-pressed break out
            break

    # close output window
    cv2.destroyAllWindows()

