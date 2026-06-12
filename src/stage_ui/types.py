# std
from enum import Enum, StrEnum, auto


class RadiusColor(StrEnum):
    """
    Possible color-coded radii corresponding to the marker circles.
    """

    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"


class FilterNumber(StrEnum):
    """
    Possible filter numbers.
    """

    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"


class WormResponse(StrEnum):
    """
    Enum representing the possible worm responses.
    """

    FULL = "F"
    PARTIAL = "P"
    ACKNOWLEDGE = "A"
    NO_RESPONSE = "N"


class KeyMapAction(Enum):
    """
    Actions mapped to keys.
    """

    STEP_LEFT = auto()
    STEP_RIGHT = auto()
    STEP_UP = auto()
    STEP_DOWN = auto()

    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()

    INC_SPEED = auto()
    DEC_SPEED = auto()

    QUIT = auto()
    FIRE = auto()
    DESTROY = auto()
    GRID = auto()
    SKIP_DATA = auto()
