# Worm Shooter

An in-house `pygame` and `pygame_gui` desktop app for controlling the lab microscope stage and laser. It shows the live camera feed, moves the stage, fires the laser in short heat bursts, and records each fire and the worm's response to a CSV file.

## Quickstart

This project is meant to be managed and run by [uv](https://docs.astral.sh/uv/). Before getting started make sure to install uv using the [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) on the project's website.

After installing, fetch the application's dependencies and run the app with the following two commands:

```
uv sync
uv run shooter
```

The first run may take some extra time as packages are installed, but subsequent runs should be faster. On the lab machine, `run.bat` at the repo root runs both commands for you.

Not using uv? Once the package is installed, you can run it like any other module:

```
python -m shooter
```

## CLI Options

To see all the options, run the app with the `--help` flag.

```
uv run shooter --help
```

| Flag | Values | Default | Description |
| --- | --- | --- | --- |
| `-d`, `--data-dir` | path | `AppConfig.DATA_DIR` | Directory to write CSV data files to. The directory must already exist. |
| `-i`, `--camera-index` | integer | `1` | OpenCV camera index selected by default on the start screen. |
| `--arduino-backend` | `pyserial`, `mock` | `pyserial` | How to talk to the Arduino. `mock` needs no hardware. |
| `--camera-backend` | `cv2`, `mock` | `cv2` | Where the video feed comes from. `mock` needs no camera. |
| `--data-backend` | `pandas`, `mock` | `pandas` | How data is recorded. `mock` writes no files. |

To run without any lab hardware:

```
uv run shooter --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

Everything else (speed and duration limits, the keymap, serial settings, the laser lock length) is set in `AppConfig` (`shooter/app/_config.py`).

## Controls

Keys are ignored while typing in a text field.

| Key | Action |
| --- | --- |
| `h` / `k` / `u` / `j` | Step the stage left / right / up / down |
| Arrow keys | Move the stage while held |
| `f` | Fire the laser (only when unlocked) |
| `d` | Destroy fire: a short fixed-length fire that is not followed by a response |
| `p` | Skip recording a response for the last fire |
| `[` / `]` | Decrease / increase feed contrast |
| `1` - `5` | Log a behavior: omega turn, pirouette, pause, forward, reversal |
| `Esc` | Cancel click-to-center |

| Mouse (on the video feed) | Action |
| --- | --- |
| Left click | Move the stage so the clicked point is in the center of the frame |
| Right click | Move the stage so the clicked point is under the marker |

Clicking again while the stage is still centering re-aims it. Any stage or fire key also cancels centering. Click-to-center is calibrated by `PX_PER_STEP` and `CENTER_INVERT_X`/`CENTER_INVERT_Y` in `AppConfig`.
