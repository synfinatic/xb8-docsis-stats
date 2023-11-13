VERSION := $(shell grep version pyproject.toml | sed -Ee 's/version = "(.*)"/\1/')
DOCKER_REPO=synfinatic
PROJECT_NAME=xb8-docsis-stats

.PHONY: docker
docker:
	docker buildx build \
		-t $(DOCKER_REPO)/$(PROJECT_NAME):v$(VERSION) \
		-t $(DOCKER_REPO)/$(PROJECT_NAME):latest \
		--build-arg VERSION=v$(VERSION) \
		--platform linux/arm64,linux/amd64 \
		-f Dockerfile .

docker-push:
	docker push synfinatic/xb8-docsis-stats:v$(VERSION)
	docker push synfinatic/xb8-docsis-stats:latest

