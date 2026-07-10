"""
.. include:: ../../readme.md
"""

# std
import importlib.metadata

# package info
APP_NAME: str = "Worm Shooter"
"""
The user-facing name of the application, as shown in rendered UI and log
messages.
"""

VERSION: str = importlib.metadata.version("worm_shooter")
"""
The current application version, as specified in the `pyproject.toml`.
"""
