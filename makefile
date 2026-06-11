# config
PY_FILES = src/**/*.py

.PHONY: all pre-comit run tc lint format
.SECONDARY:

all: run
pre-commit: format lint tc

run:
	uv run sync && uv run stage-ui

tc:
	uv run mypy --strict -p stage_ui

lint:
	uv run ruff check $(PY_FILES)

format:
	uv run ruff format $(PY_FILES)
