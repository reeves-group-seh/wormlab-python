# std
import dataclasses
from dataclasses import dataclass

# local
from shooter.atom import Atom


@dataclass(kw_only=True)
class AppState:
    """
    All "atomic" state shared across screens.
    """

    room_temp: Atom[float | None] = dataclasses.field(
        default_factory=lambda: Atom(None)
    )
    """
    TI room temperature in degrees celsius, selected on the start screen.
    """

    room_humidity: Atom[float | None] = dataclasses.field(
        default_factory=lambda: Atom(None)
    )
    """
    Relative room humidity as a percent, selected on the start screen.
    """
