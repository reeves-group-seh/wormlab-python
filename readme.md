# ...

## Layout

- Python Workspace
  - `axon-ui` (Axon UI): UI Framework
  - `axon-ui-kit` (Axon UI Component Kit): UI Component Kit
  - `worm-shooter` (Worm Shooter): Experiment App
  - `worm-watcher` (Worm Watcher): Analysis App

## Commands

```sh
uv run worm-shooter
uv run worm-shooter --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

```sh
uv run ruff format           # format
uv run ruff check            # lint
uv run ty check              # typechecker 1
uv run mypy -p worm_shooter  # typechecker 2
uv run pdoc worm_shooter
```

```sh
rm -rf .mypy_cache/ .ruff_cache/
find packages -type d -name __pycache__ -exec rm -rf {} +
```
