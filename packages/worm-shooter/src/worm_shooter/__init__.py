"""
.. include:: ../../readme.md
"""

# std
import importlib.metadata

# package info
APP_NAME: str = "StageUI"
"""
The user-facing name of the application, as shown in rendered UI and log
messages.
"""

VERSION: str = importlib.metadata.version("stage-ui")
"""
The current application version, as specified in the `pyproject.toml`.
"""
