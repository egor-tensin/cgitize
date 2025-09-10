include prelude.mk

PROJECT := cgitize

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

.PHONY: maintenance
maintenance:
	$(MAKE) venv/upgrade

	@git_status="$$( git status --porcelain=v1 )" && \
	if [ -z "$$git_status" ]; then \
		true; \
	elif [ "$$git_status" = ' M requirements.txt' ]; then \
		git commit -am 'requirements.txt: bump dependencies' && \
			git push -q; \
	else \
		echo; \
		echo '-----------------------------------------------------------------'; \
		echo 'Error: unrecognized modifications in the repository:'; \
		echo "$$git_status"; \
		echo '-----------------------------------------------------------------'; \
		exit 1; \
	fi

.PHONY: python
python:
	$(venv_activate) && python

.PHONY: repl
repl: python

.PHONY: test
test: test/unit test/local

.PHONY: test/unit
test/unit:
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@echo Unit tests
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	python -m unittest --verbose --buffer

.PHONY: test/local
test/local:
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@echo Integration test: local
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	./test/integration/local/test.sh

.PHONY: test/docker
test/docker:
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@echo Integration test: docker
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	./test/integration/docker/test.sh

.PHONY: test/example
test/example:
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@echo Integration test: example
	@echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	./test/integration/example/test.sh

.PHONY: tag
tag:
	$(venv_activate) \
		&& pip install -q --upgrade setuptools-scm \
		&& version="$$( python -m setuptools_scm --strip-dev )" \
		&& git tag "v$$version"
