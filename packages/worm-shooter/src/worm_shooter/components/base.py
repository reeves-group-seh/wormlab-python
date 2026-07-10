# std
from abc import ABC
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar, Self, cast

# pip
from pygame import Event

# local
from worm_shooter.atom import Atom


class Component(ABC):
    # private class variables
    _build_stack: ClassVar[list[Component]] = []
    """
    Stack of components whose `__init__` is currently running. A `Component`
    constructed while the stack is non-empty is a child of the component on
    top, and is automatically tracked by it.
    """

    # instance variables
    _components: set[Component]
    _unsubs: list[Callable[[], None]]

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        self = super().__new__(cls)
        self._components = set()
        self._unsubs = list()
        return self

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Wrap every subclass `__init__` so that a component constructed inside
        another component's `__init__` is automatically tracked by that
        parent.
        """
        # parent
        super().__init_subclass__(**kwargs)

        # grab original init
        orig: Callable[..., None] = cls.__init__

        @wraps(orig)
        def wrapped(
            self: Component,
            *wargs: Any,
            **wkwargs: Any,
        ) -> None:
            # grab build stack
            stack = Component._build_stack

            # skip push/build/pop when already on the stack and currently
            # building (for super().__init__() calls)
            if stack and stack[-1] is self:
                orig(self, *wargs, **wkwargs)
                return

            # get most recently initializing component (parent)
            parent: Component | None = stack[-1] if stack else None

            # push self onto stack
            stack.append(self)

            # try-except-finally ensures stack is preserved and cleanup is
            # correct
            try:
                # call original init, and build subcomponents
                orig(self, *wargs, **wkwargs)
            except BaseException:
                # ensure an exception raising component cleans up any child
                # components it created
                self.destroy()
                raise
            finally:
                # remove self from the stack
                stack.pop()

            # add self to parent
            if parent is not None:
                parent._track(self)

        # set init to wrapped
        cast(Any, cls).__init__ = wrapped

    def _track(self, component: Component) -> None:
        """
        Register a given child component.
        """
        if component not in self._components:
            self._components.add(component)

    def bind[T](
        self,
        atom: Atom[T],
        callback: Callable[[], None],
    ) -> None:
        """
        Subscribe to an atom and register the unsubscribe function for cleanup.
        """
        self._unsubs.append(atom.subscribe(callback))

    def process_event(self, event: Event) -> None:
        """
        Proccess a given event. This cascades down to child components.
        """
        for component in self._components:
            component.process_event(event)

    def update(self, dt: float) -> None:
        """
        Update given a number of seconds since the last frame. This cascades
        down to child components.
        """
        for component in self._components:
            component.update(dt)

    def destroy(self) -> None:
        """
        Unsubscribe from all atoms and do other cleanup. This cascades down to
        child components.
        """

        # destroy child components
        for component in self._components:
            component.destroy()

        # unsubscribe
        for unsub in self._unsubs:
            unsub()

        # clear lists
        self._unsubs.clear()
        self._components.clear()
