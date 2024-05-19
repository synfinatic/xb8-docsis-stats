VERSION := $(shell grep version pyproject.toml | sed -Ee 's/version = "(.*)"/\1/')
DOCKER_REPO=synfinatic
PROJECT_NAME=xb8-docsis-stats

PLATFORMS := --platform linux/amd64,linux/arm64
.PHONY: docker docker-push tests
docker:
	docker buildx build $(PLATFORMS) \
		-t $(DOCKER_REPO)/$(PROJECT_NAME):v$(VERSION) \
		-t $(DOCKER_REPO)/$(PROJECT_NAME):latest \
		--build-arg VERSION=v$(VERSION) \
		-f Dockerfile .

docker-push:
	docker buildx build $(PLATFORMS) \
		-t synfinatic/xb8-docsis-stats:v$(VERSION) \
		-t synfinatic/xb8-docsis-stats:latest --push .

tests:
	poetry run ./tests/channel_tests.py
