.PHONY: all pre-comit run tc lint format
.SECONDARY:

all: run
pre-commit: format lint tc

run:
	uv run sync && uv run stage-ui

tc:
	uv run mypy -p stage_ui

lint:
	uv run ruff check

format:
	uv run ruff format
