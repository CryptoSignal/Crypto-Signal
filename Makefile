DOCKER_REPO_NAME ?=
DOCKER_CONTAINER_NAME ?= crypto-signal
DOCKER_IMAGE_NAME ?= ${DOCKER_REPO_NAME}${DOCKER_CONTAINER_NAME}

build:
	docker build -t ${DOCKER_IMAGE_NAME} .

run:
	docker run -it --rm --env-file .env ${DOCKER_IMAGE_NAME}
