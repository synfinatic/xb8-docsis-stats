VERSION := $(shell grep version pyproject.toml | sed -Ee 's/version = "(.*)"/\1/')

.PHONY: docker
docker:
	docker build \
		-t synfinatic/xb8-docsis-stats:v$(VERSION) \
		-t synfinatic/xb8-docsis-stats:latest .

docker-push:
	docker push synfinatic/xb8-docsis-stats:v$(VERSION)
	docker push synfinatic/xb8-docsis-stats:latest
