MAKEFLAGS += --no-builtin-rules --no-builtin-variables --warn-undefined-variables
unexport MAKEFLAGS
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

escape = $(subst ','\'',$(1))

define noexpand
ifeq ($$(origin $(1)),environment)
    $(1) := $$(value $(1))
endif
ifeq ($$(origin $(1)),environment override)
    $(1) := $$(value $(1))
endif
ifeq ($$(origin $(1)),command line)
    override $(1) := $$(value $(1))
endif
endef

.PHONY: DO
DO:

PROJECT := cgitize
# Target platforms (used by buildx):
PLATFORMS := amd64,armhf,arm64
# Docker Hub credentials:
DOCKER_USERNAME := egortensin

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

.PHONY: venv/reset
venv/reset:
	rm -rf -- '$(call escape,$(venv_dir))'
	mkdir -p -- '$(call escape,$(venv_dir))'
	python -m venv -- '$(call escape,$(venv_dir))'

.PHONY: venv
venv: venv/reset
	. '$(call escape,$(venv_dir))/bin/activate' && pip install -q -r requirements.txt

# Is there a better way?
.PHONY: venv/upgrade
venv/upgrade: venv/reset
	. '$(call escape,$(venv_dir))/bin/activate' \
		&& pip install -q . \
		&& pip uninstall -q --yes '$(call escape,$(PROJECT))' \
		&& pip freeze > requirements.txt

.PHONY: py
py: python

.PHONY: repl
repl: python

.PHONY: python
python:
	. '$(call escape,$(venv_dir))/bin/activate' && python

.PHONY: test
test:
	. '$(call escape,$(venv_dir))/bin/activate' && python -m unittest --verbose --buffer
