DOCKER_REPO_NAME ?= gcr.io/compact-factor-192404/
DOCKER_CONTAINER_NAME ?= crypto-signal
DOCKER_IMAGE_NAME ?= ${DOCKER_REPO_NAME}${DOCKER_CONTAINER_NAME}
GIT_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

build:
	docker build -t ${DOCKER_IMAGE_NAME}:${GIT_BRANCH} .

publish:
	docker push ${DOCKER_IMAGE_NAME}

run:
	docker run -it --rm --env-file settings.env ${DOCKER_IMAGE_NAME}
