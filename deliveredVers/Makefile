NAME        = fly-in
PYTHON      = python3
VENV        = venv
VENV_BIN    = $(VENV)/bin
PIP         = $(VENV_BIN)/pip
PY          = $(VENV_BIN)/python


.PHONY: all run venv install debug lint lint-strict clean fclean re

all: install

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(PY) main.py

debug: install
	$(PY) -m pdb main.py

lint: install
	$(VENV_BIN)/flake8 *.py
	$(VENV_BIN)/mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# stricter type checking; run with: make lint-strict
lint-strict: install
	$(VENV_BIN)/flake8 *.py
	$(VENV_BIN)/mypy *.py --strict

# deletes all pycaches                               without triggering useless warnings
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache

fclean: clean
	rm -rf $(VENV)

re: fclean all

.DEFAULT_GOAL := run
