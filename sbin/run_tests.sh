#!/bin/bash

echo "Running tests"

# Go to the right path
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

echo "Running tests..."
cd "${DIR}/.."
pytest -vv -s -x --cov=. --cov-report xml --cov-report html tests/*.py
