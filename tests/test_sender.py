from scarecrow_client.client.sender import run_camera
import pytest
from vidgear.gears import NetGear
import multiprocessing as mp
import time
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
def zmq_receiver(zmq_args):
    client = NetGear(address=zmq_args['ip'], port=zmq_args['port'],
                     protocol=zmq_args['protocol'],
                     pattern=zmq_args['pattern'], receive_mode=True, logging=True)

    yield client
    # Close
    client.close()


def test_run_camera(zmq_args, zmq_receiver):
    p = mp.Process(target=run_camera, args=(RESOURCE_PATH+'/tests/walking_test_5s.mp4',
                                            zmq_args['ip'],
                                            zmq_args['port'],
                                            zmq_args['protocol'],
                                            zmq_args['pattern'],
                                            zmq_args['fps'], ))
    p.start()
    p.Daemon = True
    # Receive
    logger.info('Starting receiver')
    frames = []
    for i in range(5):
        frame = zmq_receiver.recv()
        logger.info('Image received')
        frames.append(frame)
        time.sleep(1)
    logger.info('Shutdown')
    p.terminate()
    p.join()
    assert len(frames) == 5
    for f in frames:
        print(f)
