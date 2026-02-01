# item imports
from dataclasses import dataclass

# local module imports
import constants

# local item imports
from direction import Direction


@dataclass
class State:

    #
    # attributes
    #

    speed: float = constants.DEFAULT_SPEED
    """
    Stage movement speed in steps per second.
    """

    move_duration: float = constants.DEFAULT_MOVE_DURATION
    """
    Duration of move commands in milliseconds.
    """

    fire_duration: float = constants.DEFAULT_FIRE_DURATION
    """
    Duration of laser fire commands in milliseconds.
    """

    grid_size: int = constants.DEFAULT_GRID_SIZE
    """
    Size of the square test grid.
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

    last_fire_time: float | None = None
    """
    Time (from `time.time()`) of the last laser fire.
    """

    last_fire_duration: float | None = None
    """
    Fire duration of the last laser fire in milliseconds.
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

    data_needed: bool = False
    """
    Whether data has yet to be recorded since the last laser fire.
    """

    direction: Direction | None = None
    """
    What direction movement is currently happening in.
    """

    running: bool = True
    """
    If the program is currently running.
    """
