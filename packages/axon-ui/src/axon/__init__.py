"""
.. include:: ../../readme.md
"""

# relative
from . import router
from ._app import App
from ._atom import Atom
from ._component import Component
from ._screen import Screen
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
]
