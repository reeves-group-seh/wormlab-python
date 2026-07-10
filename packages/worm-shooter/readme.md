# Worm Shooter

An in-house `pygame` and `pygame_gui` desktop app for controlling the lab microscope stage and laser.

## Quickstart

This project is meant to be managed and run by [uv](https://docs.astral.sh/uv/). Before getting started make sure to install uv using the [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) on the project's website.

After installing, fetch the application's dependencies and run the app with the following two commands:

```
uv sync
uv run worm-shooter
```

The first run may take some extra time as packages are installed, but subsequent runs should be faster.

Not using uv? Once the package is installed, you can run it like any other module:

```
python -m worm_shooter
```

## CLI Options

There are a number of CLI flags that customize the application. To see all the options, run the module with the `--help` flag.

```
python -m worm_shooter --help
```

...

## Project Philosophy

...
