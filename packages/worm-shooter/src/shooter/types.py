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

    FULL = "full"
    PARTIAL = "partial"
    ACKNOWLEDGE = "acknowledge"
    PAUSE = "pause"
    NO_RESPONSE = "no_response"


class WormBehavior(StrEnum):
    """
    Enum representing possible worm behaviors exhibited between fires.
    """

    OMEGA = "omega_turn"  # OME
    PIROUETTE = "pirouette"  # PIR
    PAUSE = "pause"  # PAU
    FORWARD = "forward"  # FOR
    REVERSAL = "reversal"


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


class LaserLockPhase(Enum):
    """
    Where a laser fire is in the flash/lock/unlocked cycle.
    """

    UNLOCKED = enum.auto()
    FIRING = enum.auto()
    LOCKED = enum.auto()


@dataclass(frozen=True, kw_only=True)
class LaserLock:
    """
    The current lock phase derived from a `LaserFire`, plus the time left in
    that phase (0 when `UNLOCKED`) and if data needs to be recorded.
    """

    phase: LaserLockPhase
    remaining: float
    data_needed: bool


def laser_lock(
    fire: LaserFire | None,
    *,
    flash_duration: float,
    lock_duration: float,
    data_needed: bool,
) -> LaserLock:
    """
    Compute the current `LaserLock` for a fire, given how long the flash and
    lock (cooldown) phases last.

    :param fire: The most recent fire, or `None` if the laser has never been
        fired.

    :param flash_duration: How long, in seconds, the flash phase lasts after
        `fire.time`.

    :param lock_duration: How long, in seconds, the lock (cooldown) phase lasts
        after the flash phase ends.

    :param data_needed: `HomeState.data_needed` value for deriving whether to
        stay locked.
    """

    # no fires, unlocked by default
    if fire is None:
        return LaserLock(
            phase=LaserLockPhase.UNLOCKED,
            remaining=0.0,
            data_needed=data_needed,
        )

    # calculate total elapsed time since fire
    elapsed = (dt.datetime.now().astimezone() - fire.time).total_seconds()

    # when elapsed is less than flash duration, in fire flash phase
    if elapsed < flash_duration:
        return LaserLock(
            phase=LaserLockPhase.FIRING,
            remaining=flash_duration - elapsed,
            data_needed=data_needed,
        )

    # calculate total duration of flash + countdown
    total_duration = flash_duration + lock_duration

    # when elapsed is less than total duration, locked bc countdown
    if elapsed < total_duration:
        return LaserLock(
            phase=LaserLockPhase.LOCKED,
            remaining=total_duration - elapsed,
            data_needed=data_needed,
        )

    # when time elapsed but no data, stay locked
    if data_needed:
        return LaserLock(
            phase=LaserLockPhase.LOCKED,
            remaining=0.0,
            data_needed=data_needed,
        )

    # otherwise, unlocked
    return LaserLock(
        phase=LaserLockPhase.UNLOCKED,
        remaining=0.0,
        data_needed=data_needed,
    )
