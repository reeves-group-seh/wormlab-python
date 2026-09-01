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


class StepDirection(Enum):
    """
    Direction of a single axis-aligned stage movement.
    """

    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()


@dataclass(frozen=True, kw_only=True)
class CenterPlan:
    """
    The movements still to be sent to bring a clicked point to a target.

    Each entry in `moves` is one stage command. Because a command's speed and
    duration are fixed, every command covers the same distance, so a leg of the
    journey is a whole number of them: the x leg first, then the y leg.

    A plan is immutable and is consumed with `pop`, which hands back the next
    move and whatever is left. Dropping the remainder cancels the rest of the
    journey, which is how a keypress interrupts one.
    """

    moves: tuple[StepDirection, ...]

    def pop(self) -> tuple[StepDirection, CenterPlan | None]:
        """
        Split off the next move.

        :return: The move to send now, and the rest of the plan, or `None` when
            this was the last one.
        """
        head, *tail = self.moves
        return head, CenterPlan(moves=tuple(tail)) if tail else None


def center_plan(
    point: tuple[int, int],
    *,
    target: tuple[int, int],
    px_per_command: float,
    invert_x: bool,
    invert_y: bool,
    max_commands: int,
) -> CenterPlan | None:
    """
    Build the plan that brings `point` onto `target`, both in plane
    coordinates.

    The gap is divided into whole commands, so the stage lands within half a
    command of the target rather than exactly on it. A gap smaller than half a
    command rounds to no movement at all.

    :param point: The clicked position, in plane coordinates.

    :param target: Where that position should end up, in plane coordinates.

    :param px_per_command: How far, in plane units, one command moves the
        image. This is the stage speed times the command duration times the
        `PX_PER_STEP` calibration constant.

    :param invert_x: Flip the x direction, for a stage whose left/right wiring
        runs opposite to the default assumption that the image moves the way
        the stage does.

    :param invert_y: Flip the y direction. See `invert_x`.

    :param max_commands: Refuse to plan a journey longer than this many
        commands, guarding against a mis-set calibration constant.

    :return: The plan, or `None` when the point is already close enough, the
        journey would be too long, or a command covers no ground.
    """

    # a command that covers no ground would never arrive
    if px_per_command <= 0.0:
        return None

    # how far the point has to travel, in plane units. y grows downwards
    dx = target[0] - point[0]
    dy = target[1] - point[1]

    # the image moves the way the stage does, so a direction is just the sign
    # of its gap, with the invert flags flipping an axis that is wired the
    # other way round
    x_dir = StepDirection.RIGHT if (dx > 0) != invert_x else StepDirection.LEFT
    y_dir = StepDirection.DOWN if (dy > 0) != invert_y else StepDirection.UP

    # every command covers the same ground, so each leg is a count of them
    moves = ((x_dir,) * round(abs(dx) / px_per_command)) + (
        (y_dir,) * round(abs(dy) / px_per_command)
    )

    # already there, near enough
    if not moves:
        return None

    # far enough that the calibration constant is more likely wrong than the
    # click, so do nothing rather than send the stage on a long trip
    if len(moves) > max_commands:
        return None

    return CenterPlan(moves=moves)


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
