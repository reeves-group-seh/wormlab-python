# std
import datetime as dt
from dataclasses import dataclass
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

    FIRE = auto()
    DESTROY = auto()
    GRID = auto()
    SKIP_DATA = auto()


@dataclass(frozen=True, kw_only=True)
class LaserFire:
    """
    Information about a laser fire itself. This is just the observable data that
    is know at fire time and cannot be changed.
    """

    time: dt.datetime
    duration: float

    @staticmethod
    def new(duration: float) -> LaserFire:
        return LaserFire(
            time=dt.datetime.now().astimezone(),
            duration=duration,
        )
