#!/bin/bash
if [[ $# -ge 1 ]]; then 
  INPUT="${1}"
else
  INPUT="tests/resources/walking_test_5s.mp4"
fi
echo "Start server with input: ${INPUT}"
cd ..
python3 -m client.sender --input "${INPUT}"
