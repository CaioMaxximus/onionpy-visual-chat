SHELL := /bin/bash

PYTHON_CMD := $(shell command -v python3 2>/dev/null || which python3 2>/dev/null || command -v python 2>/dev/null || which python 2>/dev/null)
VENV_PYTHON = venv/bin/python
PIP = venv/bin/pip

PYTHON = $(PYTHON_CMD)
LOCAL_PYTHON = $(VENV_PYTHON)
INSTALL_SCRIPT = set_docker_env.py

run:

	@export APPLICATION_ROOT="$$(pwd)" && \
	PYTHONPATH=src $(LOCAL_PYTHON) -m root

install:
	$(PYTHON) -m venv venv && \
	$(PIP) install -r requirements.txt && \
	$(LOCAL_PYTHON) $(INSTALL_SCRIPT)
