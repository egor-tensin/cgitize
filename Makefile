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
