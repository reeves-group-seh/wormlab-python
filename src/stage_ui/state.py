# module imports
import time

# item imports
from dataclasses import dataclass

# local item imports
from serial_bridge import Direction


#
# constants
#


SPEED_STEP: float = 10.0
"""
Value to increment and decrement speed by.
"""

MIN_SPEED: float = 10.0
"""
Minimum stage movement speed in steps per second.
"""

MAX_SPEED: float = 1000.0
"""
Maximum stage movement speed in steps per second.
"""

DEFAULT_SPEED: float = 100.0
"""
Default stage movement speed in steps per second.
"""

MIN_MOVE_DURATION: float = 1.0
"""
Mimimum stage move duration in milliseconds.
"""

MAX_MOVE_DURATION: float = 5000.0
"""
Maximum stage move duration in milliseconds.
"""

DEFAULT_MOVE_DURATION: float = 100.0
"""
Default stage move duration in milliseconds.
"""

MIN_FIRE_DURATION: float = 1.0
"""
Mimimum laser fire duration in milliseconds.
"""

MAX_FIRE_DURATION: float = 10000.0
"""
Maximum laser fire duration in milliseconds.
"""

DEFAULT_FIRE_DURATION: float = 200.0
"""
Default laser fire duration in milliseconds.
"""

MIN_GRID_SIZE: int = 1
"""
Minumum size of the square test grid.
"""

MAX_GRID_SIZE: int = 20
"""
Maximum size of the square test grid.
"""

DEFAULT_GRID_SIZE: int = 3
"""
Default size of the square test grid.
"""

#
# classes
#


@dataclass
class State:
    """
    Representation of all mutable application state.
    """

    #
    # attributes
    #

    _speed: float = DEFAULT_SPEED
    """
    Stage movement speed in steps per second.
    """

    _move_duration: float = DEFAULT_MOVE_DURATION
    """
    Duration of move commands in milliseconds.
    """

    _fire_duration: float = DEFAULT_FIRE_DURATION
    """
    Duration of laser fire commands in milliseconds.
    """

    _grid_size: int = DEFAULT_GRID_SIZE
    """
    Size of the square test grid.
    """

    _fire_instance: _FireInstance | None = None
    """
    The last laser fire that has yet to be recorded.
    """

    place_marker: bool = False
    """
    If the app is in "marker placement" mode. When `True`, mouse can be used to
    place marker on camera grid.
    """

    pos_vid: tuple[float, float] | None = None
    """
    The "normalized coords" of where mouse click placed a marker.
    """

    flash_start_time: float | None = None
    """
    Time (from `time.time()`) when flash started or None when not flashing.
    """

    room_temp: float | None = None
    """
    Room temperature in degrees celsius.
    """

    worm_strain: str | None = None
    """
    Current worm strain.
    """

    worm_id: str | None = None
    """
    Current index or ID of the worm being recorded.
    """

    direction: Direction | None = None
    """
    What direction movement is currently happening in.
    """

    running: bool = True
    """
    If the program is currently running.
    """

    #
    # speed methods
    #

    @property
    def speed(self) -> float:
        """
        Stage movement speed in steps per second.
        """
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = max(MIN_SPEED, min(MAX_SPEED, value))

    def speed_increment(self) -> None:
        """
        Increment the value of movement speed by a standard value.
        """
        self.speed = self.speed + SPEED_STEP

    def speed_decrement(self) -> None:
        """
        Decrement the value of movement speed by a standard value.
        """
        self.speed = self.speed - SPEED_STEP

    #
    # move_duration methods
    #

    @property
    def move_duration(self) -> float:
        """
        Duration of move commands in milliseconds.
        """
        return self._move_duration

    @move_duration.setter
    def move_duration(self, value: float) -> None:
        self._move_duration = max(MIN_MOVE_DURATION, min(MAX_MOVE_DURATION, value))

    #
    # fire_duration methods
    #

    @property
    def fire_duration(self) -> float:
        """
        Duration of laser fire commands in milliseconds.
        """
        return self._fire_duration

    @fire_duration.setter
    def fire_duration(self, value: float) -> None:
        self._fire_duration = max(MIN_FIRE_DURATION, min(MAX_FIRE_DURATION, value))

    #
    # grid_size methods
    #

    @property
    def grid_size(self) -> int:
        """
        Size of the square test grid.
        """
        return self._grid_size

    @grid_size.setter
    def grid_size(self, value: int) -> None:
        self._grid_size = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, value))

    #
    # fire_instance methods
    #

    @property
    def data_needed(self) -> bool:
        """
        Whether data has yet to be recorded since the last laser fire.
        """
        return self._fire_instance is not None

    @property
    def last_fire_time(self) -> float | None:
        """
        Time (from `time.time()`) of the last laser fire.
        """
        return (
            self._fire_instance.fire_time if self._fire_instance is not None else None
        )

    @property
    def last_fire_duration(self) -> float | None:
        """
        Fire duration of the last laser fire in milliseconds.
        """
        return (
            self._fire_instance.fire_duration
            if self._fire_instance is not None
            else None
        )

    #
    # data collection related methods
    #

    def laser_fired(self, fire_duration: float, fire_time: float | None = None) -> None:
        """
        Update state to reflect a laser fire.

        :type fire_duration: float
        :param fire_duration:
            The time in milliseconds that the laser was fired for.

        :type fire_time: float | None
        :param fire_time:
            The time (from `time.time()`) that the laser was fired at. If
            `None`, the current time is used.
        """

        # ensure fire_time is set
        if fire_time is None:
            fire_time = time.time()

        # update state
        self._fire_instance = _FireInstance(fire_time, fire_duration)

    def data_recorded(self) -> None:
        """
        Update state to reflect data has been recorded.
        """

        # update state
        self._fire_instance = None


@dataclass
class _FireInstance:
    """
    Record of a laser fire.
    """

    #
    # attributes
    #

    fire_time: float
    """
    Time (from `time.time()`) that the laser was fired at.
    """

    fire_duration: float
    """
    Duration in milliseconds that the laser was fired for.
    """
