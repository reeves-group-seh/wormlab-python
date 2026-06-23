# std
from abc import ABC
from collections.abc import Callable

# pip
from pygame import Event
from pygame_gui.core import UIElement

# local
from stage_ui.atom import Atom


class Component(ABC):
    def __init__(self) -> None:
        # store values
        self._elements: list[UIElement | Component] = []
        self._unsubs: list[Callable[[], None]] = []

    def track[E: UIElement | Component](self, element: E) -> E:
        """
        Register a given element / component.
        """
        self._elements.append(element)
        return element

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
        Proccess a given event. By default, it calls `process_event` on all
        child components.
        """
        for element in self._elements:
            if isinstance(element, Component):
                element.process_event(event)

    def update(self, dt: float) -> None:
        """
        Update given a number of seconds since the last frame. By default, it
        calls `update` on all child components.
        """
        for element in self._elements:
            if isinstance(element, Component):
                element.update(dt)

    def kill(self) -> None:
        """
        Destroy all the elements and unsubscribe from any state.
        """

        # kill elements and unsubscribe
        for element in self._elements:
            element.kill()
        for unsub in self._unsubs:
            unsub()

        # clear lists
        self._unsubs.clear()
        self._elements.clear()
