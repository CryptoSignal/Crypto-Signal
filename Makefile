DOCKER_REPO_NAME ?=
DOCKER_CONTAINER_NAME ?= crypto-signal
DOCKER_IMAGE_NAME ?= ${DOCKER_REPO_NAME}${DOCKER_CONTAINER_NAME}

build:
	docker rm crypto-signal
	docker build -t ${DOCKER_IMAGE_NAME} .
	docker create --name=crypto-signal crypto-signal:latest
	docker cp crypto-signal:/app/behaviours/ui/www/static/index.js ./app/behaviours/ui/www/static/index.js
run: 
	docker run -it --rm --env-file .env ${DOCKER_IMAGE_NAME}
