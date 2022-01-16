import time
import configparser
import multiprocessing as mp
from vidgear.gears import NetGear
import pytest
from scarecrow_server.server.receiver import receive, main
from vidgear.gears import VideoGear
from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

RESOURCE_PATH='./resources'

@pytest.fixture
def zmq_args():
    args = {}
    args['ip'] = '127.0.0.1'
    args['port'] = '5454'
    args['protocol'] = 'tcp'
    args['fps'] = 10
    args['pattern'] = 0
    return args


@pytest.fixture
def zmq_sender(zmq_args):
    stream = VideoGear(source=RESOURCE_PATH+'/tests/walking_test_5s.mp4',
                       framerate=zmq_args['fps']).start()
    server = NetGear(address=zmq_args['ip'], port=zmq_args['port'],
                     protocol=zmq_args['protocol'],
                     pattern=zmq_args['pattern'], receive_mode=False, logging=True)

    yield (stream, server)
    # Close
    stream.stop()


def __main_proc_wrap__(conf, detection_threshold, fps, ret_list):
    __res__ = {
        'res': 0,
        'det': 0
    }
    for res in main(conf, conf_path=RESOURCE_PATH+'/tests', detection_threshold=detection_threshold, fps=fps, label_path=conf['Tensorflow']['LabelMapPath'],):
        logger.info('Got res {}'.format(res))
        __res__['res'] += 1
        if res:
            __res__['det'] += 1
        ret_list.append(__res__)

def test_run_camera(zmq_args, zmq_sender):
    # Conf
    conf = configparser.ConfigParser()
    conf.read(RESOURCE_PATH+'/tests/config.ini')
    # Receive
    manager = mp.Manager()
    ret_list = manager.list()
    p = mp.Process(target=__main_proc_wrap__, args=(conf,
                                                    -1, # detection_threshold
                                                    20, # fps
                                                    ret_list,  # ret_list
                                                    ))
    p.start()
    p.Daemon = True
    # Send
    logger.info('Starting sender')
    for i in range(5):
        frame = zmq_sender[0].read()
        logger.info(f'Sending frame: {frame[:1]}')
        zmq_sender[1].send(frame)
        time.sleep(1)
    logger.info('Shutdown')
    p.terminate()
    p.join()
    logger.info('test_run_camera: {}'.format(ret_list))
    assert ret_list[-1]['res'] >= 3
    assert ret_list[-1]['det'] >= 3 # TODO: are we dropping frames with the new vidgear version?


def test_threshold(zmq_args, zmq_sender):
    # Conf
    conf = configparser.ConfigParser()
    conf.read(RESOURCE_PATH+'/tests/config.ini')
    # Receive
    manager = mp.Manager()
    ret_list = manager.list()
    p = mp.Process(target=__main_proc_wrap__, args=(conf,
                                                    1, # detection_threshold
                                                    20, # fps
                                                    ret_list,  # ret_list
                                                    ))
    p.start()
    p.Daemon = True
    # Send
    logger.info('Starting sender')
    for i in range(5):
        frame = zmq_sender[0].read()
        logger.info('Sending frame')
        zmq_sender[1].send(frame)
        time.sleep(1)
    logger.info('Shutdown')
    p.terminate()
    p.join()
    logger.info(ret_list)
    assert ret_list[-1]['res'] == 1
    assert ret_list[-1]['det'] == 1