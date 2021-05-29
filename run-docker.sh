#!/bin/bash -e

docker build -t script_examples .
docker run --rm -it \
    --volume "$(pwd):/example_scripts" \
    script_examples "$@"

