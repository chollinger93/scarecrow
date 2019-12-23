
import sys
sys.path.append('..')
import time
import multiprocessing as mp
from vidgear.gears import NetGear
import pytest
from client.sender import run_camera


@pytest.fixture
def zmq_args():
    args = {}
    args['ip'] = '127.0.0.1'
    args['port'] = '5454'
    args['protocol'] = 'tcp'
    args['fps'] = 10
    return args


@pytest.fixture
def zmq_receiver(zmq_args):
    client = NetGear(address=zmq_args['ip'], port=zmq_args['port'],
                     protocol=zmq_args['protocol'],
                     pattern=0, receive_mode=True, logging=True)

    yield client
    # Close
    client.close()


def test_run_camera(zmq_args, zmq_receiver):
    p = mp.Process(target=run_camera, args=('./resources/walking_test_5s.mp4',
                                              zmq_args['ip'],
                                              zmq_args['port'],
                                              zmq_args['protocol'],
                                              zmq_args['fps'], ))
    p.start()
    p.Daemon = True
    # Receive
    print('Starting receiver')
    for i in range(5):
        frame = zmq_receiver.recv()
        assert frame is not None
        print('Image received')
        time.sleep(1)
    print('Shutdown')
    p.terminate()
    p.join()

