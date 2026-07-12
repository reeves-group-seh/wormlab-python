# std
from abc import ABC
from enum import Enum
from typing import final

# extern
import pygame
import pygame_gui

# relative
from ._component import Component


class Screen[T: Enum](ABC):
    """
    Base class for a full-window view in the render loop.

    A `Screen` is one top-level "page" of the app. The router shows exactly one
    at a time and drives it each frame via `process_event`, `update`, and
    `draw_ui`. Each screen pairs a `pygame_gui.UIManager` with a single root
    `Component` that holds its UI tree; `process_event` and `update` step both
    the manager and the root, while `draw_ui` renders through the manager alone
    (the component tree has no draw path of its own). Many screens only need to
    build their root component and override the hooks they care about.

    The type parameter `T` is the screen-id `Enum` used to identify screens. A
    screen requests a transition by returning a member of `T` from
    `on_process_event`; returning `None` stays on the current screen.

    ## Lifecycle

    - `on_enter`: called when the screen becomes active.
    - `on_exit`: called when switching away.
    - `process_event` / `update` / `draw_ui`: called every frame while the
      screen is active.

    Subclasses build their UI as a single root `Component` and pass it to
    `super().__init__`. `process_event`, `update`, `draw_ui`, and `destroy` are
    `final` and must not be overridden; each drives the manager and/or root
    component itself (`draw_ui` renders through the manager only, `destroy`
    tears down the root only). Add per-screen behavior by overriding the hooks:

    - `on_process_event`: react to input and drive navigation (return a `T` to
      switch screens).
    - `on_update`: per-frame logic.
    - `on_destroy`: screen-level teardown.
    - `on_enter` / `on_exit`: activation and deactivation.

    Hooks default to no-ops and do not need a `super()` call.
    """

    # instance variables
    _manager: pygame_gui.UIManager
    _root: Component

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        root: Component,
    ) -> None:
        """
        Create a screen bound to a UI manager, and root component.

        :param manager: The `pygame_gui.UIManager` that owns this screen's UI
            elements and is stepped each frame.
        :param root: The root `Component` holding this screen's UI tree. The
            lifecycle methods cascade to it.
        """
        # set attributes
        self._manager = manager
        self._root = root

    def on_enter(self) -> None:
        """
        Hook called when the screen becomes active.

        Override to acquire resources or refresh state on entry. The default
        implementation does nothing.
        """
        pass

    def on_exit(self) -> None:
        """
        Hook called when switching away from this screen.

        Override to pause or release per-screen resources. The default
        implementation does nothing.
        """
        pass

    @final
    def process_event(self, event: pygame.Event) -> T | None:
        """
        Handle a render-loop event and optionally request a screen change.

        Runs `on_process_event` first. If it returns a screen id, that id is
        returned immediately and the event is *not* passed to the UI manager or
        root component; otherwise the event is forwarded to the
        `pygame_gui.UIManager` and the root component.

        :param event: The `pygame` event to handle.
        :return: The id of the screen to switch to, or `None` to stay on the
            current screen.
        """

        # pass to hook
        id = self.on_process_event(event)
        if id is not None:
            return id

        # let ui manager handle events
        self._manager.process_events(event)

        # let root component handle events
        self._root.process_event(event)

        # don't switch
        return None

    def on_process_event(self, event: pygame.Event) -> T | None:
        """
        Hook for handling an event and optionally driving navigation.

        Called by `process_event` before the UI manager and root component see
        the event. Return a member of `T` to switch to that screen. Doing so
        consumes the event, so the UI manager and root component will not
        receive it. Return `None` (the default) to let the event flow through
        and stay on the current screen.

        :param event: The `pygame` event to handle.
        :return: The id of the screen to switch to, or `None` to take no
            navigation action.
        """
        return None

    @final
    def update(self, dt: float) -> None:
        """
        Advance the screen one frame.

        Runs `on_update`, then steps the `pygame_gui.UIManager` and the root
        component.

        :param dt: Seconds elapsed since the last frame.
        """

        # pass to hook
        self.on_update(dt)

        # update ui manager
        self._manager.update(dt)

        # update root component
        self._root.update(dt)

    def on_update(self, dt: float) -> None:
        """
        Hook to advance the screen's state one frame.

        Called by `update` before the UI manager and root component are stepped.
        Override for per-frame logic; the default implementation does nothing.

        :param dt: Seconds elapsed since the last frame.
        """
        pass

    @final
    def draw_ui(self, window: pygame.Surface) -> None:
        """
        Draw the screen's UI onto the given surface.

        Called once per frame after render logic.

        :param window: The surface to draw the screen's UI onto.
        """
        self._manager.draw_ui(window)

    @final
    def destroy(self) -> None:
        """
        Tear down the screen, then run `on_destroy`.

        Destroys the root component, cascading `Component.destroy` through the
        UI tree and releasing every atom subscription made via `bind` -- then
        calls `on_destroy`.
        """
        self._root.destroy()
        self.on_destroy()

    def on_destroy(self) -> None:
        """
        Hook for performing screen-level teardown.

        Called by `destroy` after the root component has been destroyed.
        Override to release resources the screen owns; the default
        implementation does nothing.
        """
        pass
