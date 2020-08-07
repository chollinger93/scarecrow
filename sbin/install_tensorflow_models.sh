#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ppath=$(pwd)

cd "${DIR}/.."
# Clone
if [ -d "./models/" ]; then
    echo "models exists already, not cloning!"
else
    echo "Cloning models to ${ppath}"
    git submodule update --init --recursive
    git submodule update --remote
fi
# Install
if [ -z $(pip3 list | grep object_detection) ]; then
    echo "Installing models"
    cd models/research
    protoc object_detection/protos/*.proto --python_out=.
    python3 setup.py build 
    python3 setup.py install 
else
    echo "Models already installed, not updating"
fi 
cd -