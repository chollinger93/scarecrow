#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ppath=$(pwd)

cd "${DIR}/.."
if [ -d "./models/" ]; then
    echo "models exists already, not installing!"
else
    echo "Cloning models to ${ppath}"
    git submodule update --init --recursive
    git submodule update --remote
    cd models/research
    protoc object_detection/protos/*.proto --python_out=.
    python3 setup.py build 
    python3 setup.py install 
fi
cd -