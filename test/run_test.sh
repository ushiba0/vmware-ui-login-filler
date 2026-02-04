#!/bin/bash

set -eu
#set -eux

CONTAINER_NAME=vmw_loginfiller_test
CONTAINER_IMAGE_NAME=vmw_test_appliance

## Build docker image.
echo Building Docker image for vCenter Server.
cp ../main.py ./vmw_appliance_docker
docker build -t $CONTAINER_IMAGE_NAME ./vmw_appliance_docker
rm ./vmw_appliance_docker/main.py

### Test vCenter Server 7.0.
#echo Running test for vCenter Server 7.0.
#docker run --rm --name "$CONTAINER_NAME" \
#    -v "$PWD/test_vc_70":/app "$CONTAINER_IMAGE_NAME" \
#    /bin/bash /app/test.sh
#
### Test vCenter Server 8.0.
#echo Running test for vCenter Server 8.0.
#docker run --rm --name "$CONTAINER_NAME" \
#    -v "$PWD/test_vc_80":/app "$CONTAINER_IMAGE_NAME" \
#    /bin/bash /app/test.sh

## Test vCenter Server 9.0.
echo Running test for vCenter Server 9.0.
docker run --rm --name "$CONTAINER_NAME" \
    -v "$PWD/test_vc_90":/app "$CONTAINER_IMAGE_NAME" \
    /bin/bash /app/test.sh
