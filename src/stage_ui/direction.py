# item imports
from enum import IntEnum


class Direction(IntEnum):
    """
    Enum representing possible directions.
    """

    LEFT = 0
    RIGHT = 1
    DOWN = 2  # away (up)
    UP = 3  # towards

    DEFAULT = LEFT
    """
    A default value for when this enum is needed but its value unused.
    """
