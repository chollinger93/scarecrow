#!/bin/bash

echo "Running tests"

# Go to the right path
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

echo "Running server tests..."
cd "${DIR}/../scarecrow_server/"
pytest -vv -s tests/*.py

echo "Running client tests..."
cd cd "${DIR}/../scarecrow_server/"
pytest -vv -s tests/*.py