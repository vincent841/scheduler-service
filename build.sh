#!/usr/bin/env bash

DOCKER_VERSION=$(python src/version.py)
echo "Docker Version: ${DOCKER_VERSION}"
docker image build --platform linux/amd64 -t hatiolab/schevt-mgr:${DOCKER_VERSION} -t hatiolab/schevt-mgr:latest .
