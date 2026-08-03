# std
import dataclasses
from dataclasses import dataclass

# local
import axon


@dataclass(kw_only=True)
class AppState:
    """
    All "atomic" state shared across screens.
    """

    room_temp: axon.Atom[float | None] = dataclasses.field(
        default_factory=lambda: axon.Atom(None)
    )
    """
    TI room temperature in degrees celsius, selected on the start screen.
    """

    room_humidity: axon.Atom[float | None] = dataclasses.field(
        default_factory=lambda: axon.Atom(None)
    )
    """
    Relative room humidity as a percent, selected on the start screen.
    """
