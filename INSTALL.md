# Installation
This needs to be done on both the client (i.e., the raspberry) and the server.

# Automatic Setup
This is the preferred way to install `scarecrow`, but it might miss some platform-specific dependencies.
```
pip3 install wheel
pip3 install . --upgrade
```

# Using Docker (recommended)

![Docker](./docs/horizontal-logo-monochromatic-white.png)

Using `Docker` is the preferred way of running `scarecrow`, as it handles dependencies internally and operates within a controllable environment.

## Build Image
```
git submodule update --init --recursive && git submodule update --remote
docker build . -t scarecrow
```

## Run
Both `client` and `server` containers should be ran separately.

### Client
*Check cameras in `/dev` with `ffplay /dev/video$x`*

```
docker run -it \
    -p 5454:5454 \
    -p 5558:5558 \
    --ipc=host \
    -v $(pwd)/conf:/config \
    -v $(pwd)/audio_files:/data \
    --device=/dev/video2:/dev/video0 \
    scarecrow \
    /usr/local/bin/scarecrow_client --config /config --input 0
```

### Server
This runs `tensorflow` and opens the `zmq` listener.
```
docker run -it \
    -p 5455:5455 \
    -p 5557:5557 \
    --ipc=host \
    -v $(pwd)/conf:/config \
    -v $(pwd)/models/research/object_detection/data:/models \
    scarecrow \
    /usr/local/bin/scarecrow_server --config /config
```


# Manual
If for some reason, the `setup.py` does not work, the steps below show the manual installation route.

## Helper
A convenient installation helper is available as:
```
bash ./sbin/install_tf_vidgear.sh [server/client]
```

## Raspberry specific
**Only** of you are on a `Raspberry Pi`, run:
```
sudo apt install python3-dev python3-pip python3-venv # Python 3
pip3 install --upgrade pip opencv-contrib-python==3.4.3.18
sudo apt install libjasper-dev  libilmbase-dev libopenexr-dev libgstreamer1.0-dev libhdf5-dev libhdf5-serial-dev libharfbuzz0b ffmpeg libqtgui4 libqt4-test libatlas-base-dev # for opencv-python
pip3 install --upgrade picamera
```

You will also need to edit `/etc/pip.conf` as follows (unless you are using a more modern raspbian distribution):
```
[global]
extra-index-url=https://www.piwheels.org/simple
```

See: [https://www.piwheels.org/](https://www.piwheels.org/)

Also see [./sbin/install_raspi.sh](./sbin/install_raspi.sh) for an example on how to set up a new Raspberry.

## General Instructions

*Always use a virtual environment*
```
python3 -m venv env
source env/bin/activate
```

The Object Detection Models are **a submodule of this repository and usually do not need to be cloned manually**.

```
git submodule update --init --recursive && git submodule update --remote
```

You can, however, pull them as such:
```
# git clone https://github.com/tensorflow/models.git
git clone https://github.com/chollinger93/models.git # Contains bugfix
cd models/research
protoc object_detection/protos/*.proto --python_out=.
python3 setup.py build 
python3 setup.py install 
cd ../../
```

The `models` directory should be referred to in your `config.ini`.

The project supports multiple ways for playing audio. If you want to use `Gstreamer` and `playsound`:
```
sudo apt install libcairo2-dev libgirepository1.0-dev
pip3 install vext.gi
sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-good # Raspbian only
```

For `pygame`:
```
sudo apt install libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev 
sudo apt-get build-dep python-pygame
```

Install `ffmpeg`, if not installed already:
```
sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt update
sudo apt install ffmpeg
```

Install dependencies:
```
pip3 install -r scarecrow_server/requirements.txt # server
# OR
pip3 install -r scarecrow_client/requirements.txt # client
```

## Unit tests
```
# In either `scarecrow_client` or `scarecrow_server` or `scarecrow_core`
pytest -vv -s --cov-report html --cov=. --cov-config=.coveragerc tests
```