# std
from collections.abc import Callable


class Atom[T]:
    def __init__(self, value: T) -> None:
        self._value: T = value
        self._subs: list[Callable[[], None]] = []

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new: T) -> None:
        if self._value != new:
            self._value = new
            for cb in self._subs:
                cb()

    def subscribe(self, cb: Callable[[], None]) -> Callable[[], None]:
        self._subs.append(cb)
        return lambda: self._subs.remove(cb)

    # def derive[S](self, fn: Callable[[T], S]) -> Atom[S]:
    #     out = Atom(fn(self.value))
    #     self.subscribe()
