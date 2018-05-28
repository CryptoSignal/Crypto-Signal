DOCKER_REPO_NAME ?= shadowreaver/
DOCKER_CONTAINER_NAME ?= crypto-signal
DOCKER_IMAGE_NAME ?= ${DOCKER_REPO_NAME}${DOCKER_CONTAINER_NAME}
GIT_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

build:
	docker build -t ${DOCKER_IMAGE_NAME}:${GIT_BRANCH} .
	docker tag ${DOCKER_IMAGE_NAME}:${GIT_BRANCH} ${DOCKER_IMAGE_NAME}:latest

run:
	docker run -it --rm -v $PWD/config.yml:/app/config.yml ${DOCKER_IMAGE_NAME}
