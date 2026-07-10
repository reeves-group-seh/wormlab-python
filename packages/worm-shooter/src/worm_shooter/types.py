# std
import dataclasses
import datetime as dt
import enum
from dataclasses import dataclass
from enum import Enum, StrEnum


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

    STEP_LEFT = enum.auto()
    STEP_RIGHT = enum.auto()
    STEP_UP = enum.auto()
    STEP_DOWN = enum.auto()

    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()

    FIRE = enum.auto()
    DESTROY = enum.auto()
    GRID = enum.auto()
    SKIP_DATA = enum.auto()


@dataclass(frozen=True, kw_only=True)
class LaserFire:
    """
    Information about a laser fire itself. This is just the observable data that
    is known at fire time and cannot be changed.
    """

    time: dt.datetime = dataclasses.field(
        default_factory=lambda: dt.datetime.now().astimezone()
    )
    duration: float
