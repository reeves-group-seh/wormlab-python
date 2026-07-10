# StageUI

## Commands

```sh
uv run stage-ui
uv run stage-ui --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

```sh
uv run ruff format       # format
uv run ruff check        # lint
uv run ty check          # typechecker 1
uc run mypy -p stage_ui  # typechecker 2
```

```sh
rm -rf .mypy_cache/ .ruff_cache/
find packages -type d -name __pycache__ -exec rm -rf {} +
```
