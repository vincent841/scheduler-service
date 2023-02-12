#!/usr/bin/env bash
DOCKER_VERSION=$(python src/version.py)
echo "Docker Version: ${DOCKER_VERSION}"
docker push hatiolab/event-notification-service:${DOCKER_VERSION} && docker push hatiolab/event-notification-service:latest

