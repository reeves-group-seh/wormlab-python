"""
.. include:: ../../readme.md
"""

# std
import importlib.metadata

# relative
from ._background import Background
from ._button import Button
from ._cycle_box import CycleBox
from ._input import Input, InputStrict
from ._input_box import InputBox
from ._label import Label
from ._panel import MarginOption, Panel
from ._resources import DEFAULT_THEME
from ._spin_box import SpinBox, SpinBoxStrict
from ._text import Text

# public api
__all__ = [
    # modules (none)
    # classes
    "Background",
    "Button",
    "CycleBox",
    "InputBox",
    "Input",
    "InputStrict",
    "Label",
    "MarginOption",
    "Panel",
    "SpinBox",
    "SpinBoxStrict",
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
