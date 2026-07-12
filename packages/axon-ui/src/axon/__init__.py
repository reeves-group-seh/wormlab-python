"""
.. include:: ../../readme.md
"""

# relative
from . import router
from .app import App
from .atom import Atom
from .component import Component
from .screen import Screen

# public api
__all__ = [
    # modules
    "router",
    # types
    "Atom",
    "Component",
    "Screen",
    "App",
]
