# extern
from pygame_gui import PackageResource

# public api
__all__ = [
    # constants
    "DEFAULT_THEME",
]

DEFAULT_THEME: PackageResource = PackageResource(__name__, "theme.json")
"""
The library's default `theme.json` file for use with `pygame_gui`.
"""
