# Wormlab

Software for a lab studying the thermal escape response of _C. elegans_. The lab's microscope stage and laser deliver short bursts of heat to individual worms, and the researcher records how each worm responds. The main app, **Worm Shooter**, drives the stage and laser, shows the live camera feed, and logs every fire, response, and behavior to a CSV file.

## Packages

This repo is a [uv](https://docs.astral.sh/uv/) workspace. Each package has a distribution name (used by `uv`) and a separate import name.

| Package | Distribution | Import | Status | Purpose |
| --- | --- | --- | --- | --- |
| [Worm Shooter](packages/worm-shooter/readme.md) | `worm-shooter` | `shooter` | Active | Desktop app for controlling the stage and laser and recording worm responses |
| [Axon UI](packages/axon-ui/readme.md) | `axon-ui` | `axon` | Active | Small reactive UI framework built on `pygame` + `pygame_gui` |
| [Axon UI Kit](packages/axon-ui-kit/readme.md) | `axon-ui-kit` | `axonkit` | Active | Widget library (buttons, panels, inputs, etc.) built on Axon UI |

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs the right Python version (3.14) for you.
- For real experiments: the lab's Arduino-controlled stage and laser (over USB serial) and the microscope camera. Both can be replaced with mock backends for development (see below).

The lab machine runs Windows. Development works on any OS that `pygame` and OpenCV support.

## Running Worm Shooter

### On the lab machine

The lab machine should always run the `stable` branch, which tracks the latest release:

```bash
git switch stable
git pull
```

Then double-click `run.bat`. It installs any missing dependencies and starts the app. The first run takes a little longer while packages download.

### For development

```bash
uv run shooter
```

To run without any lab hardware, swap in the mock backends:

```bash
uv run shooter --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

See the Worm Shooter [readme](packages/worm-shooter/readme.md) for all CLI options, the keyboard controls, the experiment workflow, and the CSV data format.

## Development

There are no automated tests, so run the app (with mock backends if needed) to check that a change works.

Run the quality checks from the repo root:

```bash
uv run ruff format                         # format
uv run ruff check                          # lint
uv run ty check                            # typechecker 1
uv run mypy -p shooter -p axon -p axonkit  # typechecker 2
uv run pdoc shooter axon axonkit           # documentation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch and commit naming conventions, the issue -> branch -> pull request workflow, and how releases are cut.

## Contact

Maintained by Mack Rusing \<mail@mackk.net\>.
