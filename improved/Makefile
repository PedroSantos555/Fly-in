NAME        = fly-in
PYTHON      = python3
VENV        = venv
VENV_BIN    = $(VENV)/bin
PIP         = $(VENV_BIN)/pip
PY          = $(VENV_BIN)/python

# override with: make run MAP=path/to/map.txt
MAP        ?= maps/01_linear_path.txt

.PHONY: all run venv install clean fclean re

all: install

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(PY) main.py $(MAP)

# deletes all pycaches                               without triggering useless warnings
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

fclean: clean
	rm -rf $(VENV)

re: fclean all

.DEFAULT_GOAL := run
