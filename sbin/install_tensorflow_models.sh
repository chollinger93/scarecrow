#!/bin/bash
ppath=$(pwd)
if [ -d "./models/" ]; then
    echo "models exists already, not installing!"
else
    echo "Cloning models to ${ppath}"
    git clone https://github.com/otter-in-a-suit/models.git
    cd models/research
    protoc object_detection/protos/*.proto --python_out=.
    python3 setup.py build 
    python3 setup.py install 
fi
cd -