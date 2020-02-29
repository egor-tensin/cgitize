# Various one-liners which I'm too lazy to remember.
# Basically a collection of really small shell scripts.

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.SUFFIXES:

PROJECT := cgit-repos
# Enable buildx support:
export DOCKER_CLI_EXPERIMENTAL := enabled
# Target platforms (used by buildx):
platforms := linux/amd64,linux/armhf
# Docker Hub credentials:
DOCKER_USERNAME := egortensin

.PHONY: all
all: build

.PHONY: login
login:
ifndef DOCKER_PASSWORD
	$(error Please define DOCKER_PASSWORD)
endif
	@echo "$(DOCKER_PASSWORD)" | docker login --username "$(DOCKER_USERNAME)" --password-stdin

.PHONY: build
# Build natively by default.
build: docker/build

.PHONY: clean
clean:
	docker system prune --all --force --volumes

.PHONY: push
# Push multi-arch images by default.
push: buildx/push

.PHONY: check-build
check-build:
ifndef FORCE
	$(warning Going to build natively; consider `docker buildx build` instead)
endif

.PHONY: check-push
check-push:
ifndef FORCE
	$(error Please use `docker buildx build --push` instead)
endif

.PHONY: docker/build
# `docker build` has week support for multiarch repos (you need to use multiple
# Dockerfile's, create a manifest manually, etc.), so it's only here for
# testing purposes, and native builds.
docker/build: check-build
	docker build -t "$(DOCKER_USERNAME)/$(PROJECT)" .

.PHONY: docker/push
# `docker push` would replace the multiarch repo with a single image by default
# (you'd have to create a manifest and push it instead), so it's only here for
# testing purposes.
docker/push: check-push docker/build
	docker push "$(DOCKER_USERNAME)/$(PROJECT)"

# The simple way to build multiarch repos is `docker buildx`.

.PHONY: fix-binfmt
# Re-register binfmt_misc formats with the F flag (required e.g. on Bionic):
fix-binfmt:
	docker run --rm --privileged docker/binfmt:66f9012c56a8316f9244ffd7622d7c21c1f6f28d

.PHONY: buildx/create
buildx/create: fix-binfmt
	docker buildx create --use --name "$(PROJECT)_builder"

.PHONY: buildx/rm
buildx/rm:
	docker buildx rm "$(PROJECT)_builder"

.PHONY: buildx/build
buildx/build:
	docker buildx build -t "$(DOCKER_USERNAME)/$(PROJECT)" --platform "$(platforms)" --progress plain .

.PHONY: buildx/push
buildx/push:
	docker buildx build -t "$(DOCKER_USERNAME)/$(PROJECT)" --platform "$(platforms)" --progress plain --push .
