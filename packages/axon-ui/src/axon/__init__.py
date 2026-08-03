"""
.. include:: ../../readme.md
"""

# std
import importlib.metadata

# relative
from . import router
from ._app import App
from ._atom import Atom
from ._component import Component
from ._screen import Screen
from ._util import RectLike, as_rect
from ._widget import Widget

# public api
__all__ = [
    # modules
    "router",
    # types
    "Atom",
    "Component",
    "Widget",
    "Screen",
    "App",
    "RectLike",
    # functions
    "as_rect",
    # constants
]

VERSION: str = importlib.metadata.version("axon-ui")
"""
The current application version, as specified in the `pyproject.toml`.
"""
