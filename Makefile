include prelude.mk

.PHONY: DO
DO:

PROJECT := cgitize
# Target platforms (used by buildx):
PLATFORMS := amd64,armhf,arm64
# Docker Hub credentials:
DOCKER_USERNAME := egortensin
# This is still required with older Compose versions to use TARGETARCH:
export DOCKER_BUILDKIT := 1

ifdef DOCKER_PASSWORD
$(eval $(call noexpand,DOCKER_PASSWORD))
endif

.PHONY: all
all: build

.PHONY: login
login:
ifndef DOCKER_PASSWORD
	$(error Please define DOCKER_PASSWORD)
endif
	@echo '$(call escape,$(DOCKER_PASSWORD))' \
		| docker login --username '$(call escape,$(DOCKER_USERNAME))' --password-stdin

.PHONY: build
# Build natively by default.
build: compose/build

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

.PHONY: compose/build
# `docker-compose build` has week support for multiarch repos (you need to use
# multiple Dockerfile's, create a manifest manually, etc.), so it's only here
# for testing purposes, and native builds.
compose/build: check-build
	docker-compose build --progress plain

.PHONY: compose/push
# `docker-compose push` would replace the multiarch repo with a single image by
# default (you'd have to create a manifest and push it instead), so it's only
# here for testing purposes.
compose/push: check-push compose/build
	docker-compose push

.PHONY: buildx/create
buildx/create:
	docker buildx create --use --name '$(call escape,$(PROJECT))_builder'

.PHONY: buildx/rm
buildx/rm:
	docker buildx rm '$(call escape,$(PROJECT))_builder'

.PHONY: buildx/build
buildx/build:
	docker buildx build \
		-t '$(call escape,$(DOCKER_USERNAME)/$(PROJECT))' \
		-f docker/Dockerfile \
		--platform '$(call escape,$(PLATFORMS))' \
		--progress plain \
		.

.PHONY: buildx/push
buildx/push:
	docker buildx build \
		-t '$(call escape,$(DOCKER_USERNAME)/$(PROJECT))' \
		-f docker/Dockerfile \
		--platform '$(call escape,$(PLATFORMS))' \
		--progress plain \
		--push \
		.

venv_dir := .venv
venv_activate := . '$(call escape,$(venv_dir)/bin/activate)'

.PHONY: venv/reset
venv/reset:
	rm -rf -- '$(call escape,$(venv_dir))'
	mkdir -p -- '$(call escape,$(venv_dir))'
	python -m venv -- '$(call escape,$(venv_dir))'

.PHONY: venv
venv: venv/reset
	$(venv_activate) && pip install -q -r requirements.txt

# Is there a better way?
.PHONY: venv/upgrade
venv/upgrade: venv/reset
	$(venv_activate) \
		&& pip install -q . \
		&& pip uninstall -q --yes '$(call escape,$(PROJECT))' \
		&& pip freeze > requirements.txt

.PHONY: python
python:
	$(venv_activate) && python

.PHONY: repl
repl: python

.PHONY: test/unit
test/unit:
	python -m unittest --verbose --buffer

.PHONY: test/local
test/local:
	./test/integration/local/test.sh

.PHONY: test/docker
test/docker:
	./test/integration/docker/test.sh

.PHONY: test/example
test/example:
	./test/integration/example/test.sh

.PHONY: tag
tag:
	$(venv_activate) \
		&& pip install -q --upgrade setuptools-scm \
		&& version="$$( python -m setuptools_scm --strip-dev )" \
		&& git tag "v$$version"
