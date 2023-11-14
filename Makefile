VERSION := $(shell grep version pyproject.toml | sed -Ee 's/version = "(.*)"/\1/')

PLATFORMS := --platform linux/amd64,linux/arm64
.PHONY: docker
docker:
	docker buildx build $(PLATFORMS) \
		-t synfinatic/xb8-docsis-stats:v$(VERSION) \
		-t synfinatic/xb8-docsis-stats:latest .

docker-push:
	docker buildx build $(PLATFORMS) \
		-t synfinatic/xb8-docsis-stats:v$(VERSION) \
		-t synfinatic/xb8-docsis-stats:latest --push .
