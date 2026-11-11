PYTHON ?= python3
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON := .venv/bin/python
endif

.PHONY: build test validate serve refresh status

build:
	$(PYTHON) -m semcore build

test:
	$(PYTHON) -m pytest

validate:
	$(PYTHON) -m semcore validate

serve:
	$(PYTHON) -m semcore serve --port 8000

refresh:
	$(PYTHON) -m semcore refresh

status:
	$(PYTHON) -m semcore status
