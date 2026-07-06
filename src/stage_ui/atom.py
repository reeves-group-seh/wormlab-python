# std
from collections.abc import Callable


class Atom[T]:
    """
    A callback-based state variable. Callers can "subscribe" to the variable and
    have their callback function ran everytime the value changes. Values must be
    non-mutable.
    """

    # instance vars
    _value: T
    _subs: list[Callable[[], None]]

    def __init__(self, value: T) -> None:
        self._value = value
        self._subs = []

    @property
    def value(self) -> T:
        """
        The underlying value (must be immutable).
        """
        return self._value

    @value.setter
    def value(self, new: T) -> None:
        if self._value != new:
            self._value = new
            for cb in list(self._subs):
                cb()

    def subscribe(self, cb: Callable[[], None]) -> Callable[[], None]:
        """
        Register a callback function to be ran on every update to the held
        value. Returns an "unsubscribe" lambda that can be used when the caller
        no longer wants the callback function to be ran.
        """
        self._subs.append(cb)
        return lambda: self._subs.remove(cb)
