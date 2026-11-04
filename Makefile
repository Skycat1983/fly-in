PYTHON ?= python3
MAP ?= maps/easy/01_linear_path.txt

.PHONY: install run debug test lint lint-strict clean

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

clean:
	rm -rf __pycache__ parse/__pycache__ tests/__pycache__ .pytest_cache .mypy_cache
