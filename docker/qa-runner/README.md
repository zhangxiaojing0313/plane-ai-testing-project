# QA Runner Agent — Usage
#
# This directory contains the Docker infrastructure for the Plane QA Runner:
# an isolated Jenkins inbound agent with all test dependencies.
#
# Files:
#   Dockerfile         — Agent image definition
#   verify-runner.sh   — Environment verification script (runs inside container)
#
# Build:
#   docker build -t plane-qa-runner:day4 -f docker/qa-runner/Dockerfile .
#
# Local verify (no Jenkins):
#   DOCKER_GID=$(getent group docker | cut -d: -f3)
#   docker run --rm \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     --group-add $DOCKER_GID \
#     --add-host host.docker.internal:host-gateway \
#     -v /home/tester/qa-workspace/plane-ai-testing-project:/opt/plane-source:ro \
#     -e QA_VENV=/home/jenkins/qa-venv \
#     --entrypoint bash \
#     plane-qa-runner:day4 \
#     /opt/plane-source/docker/qa-runner/verify-runner.sh
#
# Run with Jenkins (see docker-compose.qa-runner.yml):
#   docker compose -f docker-compose.qa-runner.yml up -d
#
# Security notes:
#   - No .env or credentials are copied into the image
#   - Docker socket is mounted at runtime (not in image)
#   - User is non-root (jenkins)
#   - Project source is read-only
#   - Docker socket GID is passed at runtime
