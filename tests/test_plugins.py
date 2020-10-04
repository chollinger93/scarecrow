import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import pytest
from scarecrow_core.plugin_base.utils import *
from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

RESOURCE_PATH='./resources'

def load_numpy_img(inf=RESOURCE_PATH+'/tests/test_img.jpg'):
    img = Image.open(RESOURCE_PATH+'/tests/test_img.jpg')
    return np.array(img)


def rm_files_in_tree(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.abspath(os.path.join(root, file))
            os.remove(path)


@pytest.fixture
def plugs():
    yield ['audio', 'store_video']


# Namespace - TODO: fixture
ns = {}


def test_load_plugins(plugs):
    plugins = load_plugins(plugs, RESOURCE_PATH+'/tests/plugins.d')
    logger.info(plugins)
    assert 'ZmqBasePlugin' in plugins
    assert len(plugins['ZmqBasePlugin']) == 1
    assert 'ImageDetectorBasePlugin' in plugins
    assert len(plugins['ImageDetectorBasePlugin']) == 1

    ns['loaded_plugins'] = plugins


def test_start_receiver_plugins(plugs):
    procs = start_receiver_plugins(ns['loaded_plugins'])
    for p in procs:
        assert p.is_alive()
    logger.info(procs)
    assert len(procs) == 1


def test_run_image_detector_plugins_before(plugs):
    run_image_detector_plugins_before(ns['loaded_plugins'], 'server', None, None, load_numpy_img())


def test_run_image_detector_plugins_after(plugs):
    run_image_detector_plugins_after(
        ns['loaded_plugins'], 'server', None, None, True, 0, .5, load_numpy_img(RESOURCE_PATH+'/tests/test_img_labels.jpg'))


def test_run_image_detector_plugins_after_loop(plugs):
    conf = configparser.ConfigParser()
    conf.read(RESOURCE_PATH+'/tests/plugins.d/{}.ini'.format('store_video'))
    out_path = conf['Video']['Path']

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    # Remove old files
    rm_files_in_tree(out_path)

    cap = cv2.VideoCapture(RESOURCE_PATH+'/tests/walking_test_5s.mp4')
    ix = 0
    while(cap.isOpened()):
        ret, image_np = cap.read()
        if image_np is None:
            logger.warning('Image is none at ix {}'.format(ix))
            break
        ix += 1
        run_image_detector_plugins_after(
            ns['loaded_plugins'], 'server', None, None, True, ix, .5, image_np)

    # Check output path
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(out_path) if isfile(join(out_path, f))]

    assert len(files) == 2
    assert 'thumb.jpg' in list(filter(lambda s: s.endswith('jpg'), files))[0]
    assert 'output.mp4' in list(filter(lambda s: s.endswith('mp4'), files))[0]

    # TODO: check file properties
