#!/bin/bash

set -eu
#set -eux

CONTAINER_NAME=jsp_test_container
CONTAINER_IMAGE_NAME=jsp-test

## Build docker image.
docker build -t $CONTAINER_IMAGE_NAME test_vc_70 > /dev/null 2>&1

## Test vCenter Server 7.0.
echo Running test for vCenter Server 7.0.
cp ../main.py test_vc_70
docker run --rm --name "$CONTAINER_NAME" \
    -v "$PWD/test_vc_70":/app "$CONTAINER_IMAGE_NAME" \
    /bin/bash /app/test.sh

## Test vCenter Server 8.0.
echo Running test for vCenter Server 8.0.
cp ../main.py test_vc_80
docker run --rm --name "$CONTAINER_NAME" \
    -v "$PWD/test_vc_80":/app "$CONTAINER_IMAGE_NAME" \
    /bin/bash /app/test.sh

## Test vCenter Server 9.0.
echo Running test for vCenter Server 9.0.
cp ../main.py test_vc_90
docker run --rm --name "$CONTAINER_NAME" \
    -v "$PWD/test_vc_90":/app "$CONTAINER_IMAGE_NAME" \
    /bin/bash /app/test.sh

rm -f test_*/main.py