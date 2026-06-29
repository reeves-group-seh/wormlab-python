.PHONY: all pre-comit run test clean tc lint format
.SECONDARY:

all: run
pre-commit: format lint tc

run:
	uv run stage-ui

test: | test-data.tmp/
	uv run stage-ui --camera-backend=mock --arduino-backend=mock -d=test-data.tmp/

clean:
	rm -rf .mypy_cache/ .ruff_cache/ test-data.tmp/
	find src -type d -name __pycache__ -exec rm -rf {} +

tc:
	-uv run ty check
	-uv run mypy -p stage_ui

lint:
	uv run ruff check

format:
	uv run ruff format

test-data.tmp/:
	mkdir -p $@
