# ...

## Layout

- Wormlab: Python Workspace
  - Axon UI: A reactive `pygame` + `pygame_gui` library.
    - Distribution Name: `axon-ui`
    - Import Name: `axon`
  - Axon UI Component Kit: A number of components built on top of the Axon UI library.
    - Distribution Name: `axon-ui-kit`
    - Import Name: `axonkit`
  - Worm Shooter: Desktop app for controlling the lab microscope stage and laser.
    - Distribution Name: `worm-shooter`
    - Import Name: `shooter`
  - Worm Watcher: Desktop app for analyzing worm behavior.
    - Distribution Name: `worm-watcher`
    - Import Name: `watcher`

## Commands

```sh
uv run shooter
uv run shooter --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

```sh
uv run ruff format      # format
uv run ruff check       # lint
uv run ty check         # typechecker 1
uv run mypy -p shooter  # typechecker 2
uv run pdoc shooter
```

```sh
rm -rf .mypy_cache/ .ruff_cache/
find packages -type d -name __pycache__ -exec rm -rf {} +
```
