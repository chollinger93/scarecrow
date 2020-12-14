# Scarecrow-Cam
![pytest](docs/tests.svg) ![covearge](docs/codecov.svg)

A `Raspberry Pi` powered, distributed (edge) computing camera setups that runs a `Tensorflow` object detection model to determine whether a person is on the camera. The `Raspberry Pi` is used for video streaming and triggering actions (such as playing audio, turning on lights, or triggering an Arduino), whereas a server or laptop runs the object detection. With a suitable `TFLite` installation, this can happen locally on the `Raspberry` as well.

Based on the detection criteria, a **plugin model** allows to trigger downstream actions.

*Based on my [blog](https://chollinger.com/blog/2019/12/tensorflow-on-edge-or-building-a-smart-security-camera-with-a-raspberry-pi/).*

# Architecture
![Architecture](./docs/architecture.png)

![Sample](./docs/cam_1.png)

**Side note**: *The setup shown here only fits the use-case of `edge` to a degree, as we run local detection on a separate machine; technically, the Raspberry Pi is capable of running Tensorflow on board, e.g. through `TFLite` or `esp32cam`.*

*You can change this behavior by relying on a local `tensorflor` instance and having the `ZMQ` communication run over `localhost`.*

# Updates
Please see [CHANGELOG.md](./CHANGELOG.md) for details.

# Configuration and data

Copy `config/config.ini.sample` to `conf/config.ini` with the settings for your Raspberry and server.

For playing audio, please adjust `conf/plugins.d/audio.ini`.

```
[Audio]
Path=../audio_files
```
For an appropriate path.

If you want to change the `model`, please check the [Model Zoo](https://github.com/chollinger93/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md). The blog article used the outdated `ssd_mobilenet_v1_coco_2017_11_17`.

```
[Tensorflow]
ModelUrl=ssd_mobilenet_v3_large_coco_2019_08_14
LabelMapPath=./models/research/object_detection/data/mscoco_label_map.pbtxt
```

# Installing

## Requirements
This project requires:
* A Raspberry Pi + the camera module v2 (the `client`) 
* Any Linux machine on the same network (the `server`)

![Pi](./docs/pi.jpg)


## Using Docker (recommended)

![Docker](./docs/horizontal-logo-monochromatic-white.png)

Using `Docker` is the preferred way of running `scarecrow`, as it handles dependencies internally and operates within a controllable environment.

### Build Image
```
git submodule update --init --recursive && git submodule update --remote
docker build . -t scarecrow
```

### Run
Both `client` and `server` containers should be ran separately.

#### Client
*Check cameras in `/dev` with `ffplay /dev/video$x`*

```
docker run -it \
    -p 5454:5454 \
    -p 5558:5558 \
    --ipc=host \
    -v $(pwd)/conf:/config \
    -v $(pwd)/resources/audio_files:/data \
    --device=/dev/video2:/dev/video0 \
    scarecrow \
    /usr/local/bin/scarecrow_client --config /config --input 0
```

#### Server
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

## Manual install (advanced)
`scarecrow-cam` can be installed using pip:
```
pip3 install . --upgrade
```

Please see [INSTALL.md](./INSTALL.md) for details and troubleshooting.

### Run (RasPi)
```
scarecrow_client --config ./conf --input 0 # for picam
scarecrow_client --config ./conf --input ./resources/tests/walking_test_5s.mp4 # for local video 
```

### Run (Server)
```
scarecrow_server --config ./conf
```

# Plugins
A plugin model allows to trigger downstream actions. These actions are triggered based on the configuration.

Plugins can be enabled by setting the following in `config.ini`:
```
[Plugins]
Enabled=audio
Disabled=
```

Currently, the following plugins are avaibale:

| Plugin | Description                                 | Requirements                                 | Configuration              | Base  |
|--------|---------------------------------------------|----------------------------------------------|----------------------------|-------|
| `audio`  | Plays audio files once a person is detected | Either `playsound`, `pygame`, or `omxplayer` | `conf/plugins.d/audio.ini` | `ZMQ` |
| `store_video`  | Stores video files on the server, with a defined buffer or length | `Path` and `Encoding` settings | `conf/plugins.d/store_video.ini` | `ZServerMQ` |

# How to contribute
This project is in an **early state of development**. Therefore,  there are several open items that need to be covered. Please see [TODO](TODO.md) for details. 

# License
This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details.