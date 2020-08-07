#!/bin/bash

echo "Running tests"

# Go to the right path
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

echo "Running tests..."
pytest -vv -s -x --cov=. --cov-report xml --cov-report html tests/*.py
pytestStatus=$?

# Test status before CI/CD
if [ $pytestStatus -eq 0 ]; then
    anybadge -o --label=pytest --value=pass --file=docs/tests.svg pass=green fail=red
else
    anybadge -o --label=pytest --value=fail --file=docs/tests.svg pass=green fail=red
fi 

# Coverage before CI/CD
coverage=$(sed -n 2p coverage.xml | egrep -o "line-rate=\"0.([0-9]){1,4}\"" | egrep -o "[+-]?([0-9]*[.])?[0-9]+")
coverage=$(echo "$coverage*100" | bc)
anybadge -o --value=$coverage --file=docs/codecov.svg coverage