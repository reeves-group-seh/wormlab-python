"""
A minimal observable value used for reactive state across the app.

An `Atom` wraps a single immutable value and lets interested parties
*subscribe* to it. Whenever the value changes, every registered callback is
run, allowing UI components to update themselves in response to state changes
without polling. This is the primitive behind cross-screen state (see
`stage_ui.app.AppState`) and reactive `Component` updates.

Only the value stored in an `Atom` should be treated as observable; the value
itself must be immutable. Changes are detected with `!=`, so mutating a value
in place (e.g. appending to a list) will not trigger subscribers. Replace the
value instead of mutating it.

## Basic usage

Create an `Atom`, read its value, and react to changes:

```python
temp = Atom(20.0)

def on_change() -> None:
    print(f"temperature is now {temp.value}")

unsubscribe = temp.subscribe(on_change)

temp.value = 21.5  # prints: temperature is now 21.5
temp.value = 21.5  # no output; value is unchanged
temp.value = 22.0  # prints: temperature is now 22.0
```


## Unsubscribing

`Atom.subscribe` returns a callable that removes the callback when invoked. Call it
once the subscriber no longer needs updates (for example, when a component is
torn down):

```python
unsubscribe()
temp.value = 25.0  # no output; callback is no longer registered
```

## Reacting to the new value

Callbacks receive no arguments; read the current value from the `Atom`
directly inside the callback:

```python
humidity = Atom(0.4)
humidity.subscribe(lambda: label.set_text(f"{humidity.value:.0%}"))
humidity.value = 0.55  # label now reads "55%"
```
"""

# std
from collections.abc import Callable


class Atom[T]:
    """
    A callback-based state variable. Callers can "subscribe" to the variable and
    have their callback function run every time the value in replaced with an
    unequal value (compared with `!=`). Assigning an equal value, or mutating
    the current one in place does not notify. For this reason, it is recommended
    to only store immutable types.
    """

    # instance vars
    _value: T
    _subs: list[Callable[[], None]]

    def __init__(self, value: T) -> None:
        """
        Create a new `Atom` with the given value.

        :param value:
            The value for the `Atom` to store. This value should be immutable.
        """

        # set instance vars
        self._value = value
        self._subs = []

    @property
    def value(self) -> T:
        """
        The stored value (must be immutable). All registered callback functions
        are run when this value is changed.
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
        Register a callback function to be run on every update to the held
        value. Returns an "unsubscribe" lambda that can be used when the caller
        no longer wants the callback function to be ran.

        :param cb: The callback function. This is run every time the value is
            changed until the unsubscribe lambda is executed.

        :return: An unsubscribe lambda. When executed, the given callback will no
            longer be ran when the value updates.
        """
        self._subs.append(cb)
        return lambda: self._subs.remove(cb)
