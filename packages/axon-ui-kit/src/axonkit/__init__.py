"""
.. include:: ../../readme.md
"""

# std
import importlib.metadata

# relative
from ._background import Background
from ._button import Button
from ._cycle_box import CycleBox
from ._input import Input
from ._label import Label
from ._panel import Panel
from ._resources import DEFAULT_THEME
from ._spin_box import SpinBox
from ._text import Text

# public api
__all__ = [
    # modules (none)
    # classes
    "Background",
    "Button",
    "CycleBox",
    "Input",
    "Label",
    "Panel",
    "SpinBox",
    "Text",
    # constants
    "DEFAULT_THEME",
    "VERSION",
]

# package info
VERSION: str = importlib.metadata.version("axon-ui-kit")
"""
The current application version, as specified in the `pyproject.toml`.
"""
