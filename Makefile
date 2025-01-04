# Configuration:
# Only set these if they have not been defined via command-line
# such as: make VENV_NAME=my_custom_venv
VENV_NAME ?= venv
PYTHON ?= python3
PYPIRC = $(HOME)/.pypirc

# Extract PROJECT_NAME from setup.py using helper script
PROJECT_NAME := $(shell $(PYTHON) get_project_name.py)

# Default target
.DEFAULT_GOAL := test-publish

# exclude special targets that start with a dot (like .PHONY)
# exclude pattern rules that use % (like %.o: %.c)
show-make-targets:
	@grep -E '^[^.%].*[^ ]:' Makefile | cut -d: -f1 | grep -i '^[a-z]'

# Show the project name found in setup.py
show-project-name:
	@echo $(PROJECT_NAME)

# Check for ~/.pypirc
check-pypirc:
	@if [ ! -f $(PYPIRC) ]; then \
		echo "Error: $(PYPIRC) not found. Please create it with your PyPI credentials."; \
		exit 1; \
	fi

# Create and configure virtual environment
$(VENV_NAME):
	$(PYTHON) -m venv $(VENV_NAME)
	./$(VENV_NAME)/bin/pip install --upgrade pip
	./$(VENV_NAME)/bin/pip install setuptools wheel twine

# Build distribution
build: $(VENV_NAME)
	./$(VENV_NAME)/bin/python setup.py sdist bdist_wheel

# Clean build artifacts and virtual environment
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV_NAME)/
	rm -rf test-install-venv/
	rm -f *.whl.metadata .??*~
	find . -type d -name "__pycache__" -exec rm -r "{}" +
	find . -type f -name "*.pyc" -delete
	command pip cache purge

# Test PyPI targets
test-publish: clean check-pypirc $(VENV_NAME) build
	./$(VENV_NAME)/bin/twine upload --verbose --repository testpypi dist/*

test-install: clean
	$(PYTHON) -m venv test-install-venv
	./test-install-venv/bin/pip install --force-reinstall --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ $(PROJECT_NAME)

# Production PyPI targets
prod-publish: clean check-pypirc $(VENV_NAME) build
	@echo "Are you sure you want to publish to production PyPI? [y/N] " && read ans && [ $${ans:-N} = y ]
	./$(VENV_NAME)/bin/twine --verbose upload dist/*

prod-install: clean
	$(PYTHON) -m venv prod-install-venv
	./prod-install-venv/bin/pip install --force-reinstall $(PROJECT_NAME)

# Declare targets that don't create a file of the same name
.PHONY: show-make-targets show-project-name check-pypirc build clean test-publish test-install prod-publish prod-install
