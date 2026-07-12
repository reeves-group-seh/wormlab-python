# std
from abc import ABC
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar, Self, cast, final

# extern
import pygame

# relative
from ._atom import Atom


class Component(ABC):
    """
    Base class for a reusable, self-contained piece of UI.

    A `Component` owns a group of related UI elements and, optionally, other
    `Component`s nested inside it. To subclasses, it provides automatic
    parent/child tracking, a lifecycle that cascades to children
    (`process_event`, `update`, `destroy`), and managed `Atom` subscriptions via
    `bind`. Subclasses build their UI in `__init__` and add per-component
    behavior by overriding the `on_*` lifecycle hooks.

    ## Automatic child tracking

    Any `Component` constructed inside another component's `__init__` is
    automatically registered as a child of the enclosing component; there is no
    manual `add_child` call. This is driven by a build stack maintained across
    every subclass `__init__`, so nesting works out of the box:

    ```python
    class Panel(Component):
        def __init__(self) -> None:
            # tracked as a child of this Panel automatically
            self.header = Label("Temperature")
            self.readout = Readout()
    ```

    Because tracking follows the call stack, children are registered even when
    created several frames deep in helper methods called from `__init__`.

    Components should not raise an exception during construction, however, if a
    component were to raise during construction, any children already built are
    cleaned up before the exception propagates.

    ## Lifecycle

    The three lifecycle methods each cascade to every tracked child, so calling
    them on a root component drives the whole tree:

    - `process_event`: forward a `pygame` event down the tree.
    - `update`: advance state given seconds elapsed since the last frame.
    - `destroy`: tear down: destroy children, then unsubscribe from every atom
      bound via `bind`.

    These three methods are `final` and drive the cascade themselves; do not
    override them. Instead, add per-component behavior by overriding the
    matching `on_*` hook (`on_process_event`, `on_update`, `on_destroy`). Hooks
    default to no-ops and do not need a `super()` call:

    ```python
    class Readout(Component):
        def on_update(self, dt: float) -> None:
            ...  # runs each frame, before children are updated
    ```

    The cascade order differs by phase: `process_event` and `update` run this
    component's hook *before* recursing into children (top-down), while
    `destroy` tears down children *before* calling `on_destroy` (bottom-up).

    ## Reactive state

    Use `bind` to subscribe to an `Atom` rather than calling `Atom.subscribe`
    directly. `bind` records the unsubscribe callable so the subscription is
    released automatically in `destroy`, preventing dangling callbacks after the
    component is gone:

    ```python
    class Readout(Component):
        def __init__(self, temp: Atom[float]) -> None:
            self._temp = temp
            self.bind(temp, self._on_change)

        def _on_change(self) -> None:
            ...
    ```
    """

    # private class variables
    _build_stack: ClassVar[list[Component]] = []
    """
    Stack of components whose `__init__` is currently running. A `Component`
    constructed while the stack is non-empty is a child of the component on
    top, and is automatically tracked by it.
    """

    # instance variables
    _components: list[Component]
    _unsubs: list[Callable[[], None]]

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        self = super().__new__(cls)
        self._components = list()
        self._unsubs = list()
        return self

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Wrap every subclass `__init__` so that a component constructed inside
        another component's `__init__` is automatically tracked by that parent.
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
        Register a child component so it receives lifecycle cascades.

        Normally called automatically by the build stack when `component` is
        constructed inside this component's `__init__`; should not be called
        by hand. Tracking the same component twice is a no-op.

        :param component: The child component to track.
        """
        if component not in self._components:
            self._components.append(component)

    def bind[T](
        self,
        atom: Atom[T],
        callback: Callable[[], None],
    ) -> None:
        """
        Subscribe to an atom for the lifetime of this component.

        Prefer this over calling `Atom.subscribe` directly: the unsubscribe
        callable is recorded and invoked in `destroy`, so the subscription is
        released automatically when the component is torn down.

        :param atom: The atom to observe.
        :param callback: Called with no arguments whenever `atom` changes. Read
            the current value from `atom` inside the callback.
        """
        self._unsubs.append(atom.subscribe(callback))

    @final
    def process_event(self, event: pygame.Event) -> None:
        """
        Run `on_process_event`, then cascade the event to child components.

        :param event: The `pygame` event to handle.
        """
        self.on_process_event(event)
        for component in self._components:
            component.process_event(event)

    def on_process_event(self, event: pygame.Event) -> None:
        """
        Handle an event for this component.

        Called by `process_event` before the event is cascaded to child
        components. Override to react to input; the default implementation does
        nothing.

        :param event: The `pygame` event to handle.
        """
        pass

    @final
    def update(self, dt: float) -> None:
        """
        Run `on_update`, then cascade the frame update to child components.

        :param dt: Seconds elapsed since the last frame.
        """
        self.on_update(dt)
        for component in self._components:
            component.update(dt)

    def on_update(self, dt: float) -> None:
        """
        Advance this component's state one frame.

        Called by `update` once per frame, before child components are updated.
        Override for per-frame logic (animation, polling, etc.); the default
        implementation does nothing.

        :param dt: Seconds elapsed since the last frame.
        """
        pass

    @final
    def destroy(self) -> None:
        """
        Tear down this component and all of its children, then run `on_destroy`.

        Destroys every tracked child, releases every subscription made via
        `bind`, and finally calls `on_destroy`.
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

        # pass to hook
        self.on_destroy()

    def on_destroy(self) -> None:
        """
        Perform custom teardown for this component.

        Called by `destroy` after children have been destroyed and all `bind`
        subscriptions released. Override to free resources this component owns
        (surfaces, files, handles); the default implementation does nothing.
        """
        pass
