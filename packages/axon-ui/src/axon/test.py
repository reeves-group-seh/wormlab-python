from enum import Enum, auto
from typing import override

import pygame
import pygame_gui

# extern
import axon


class ScreenId(Enum):
    HOME = auto()


class Counter(axon.Component):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        count: axon.Atom[int],
    ) -> None:
        # store the atom
        self._count = count

        # create the element
        self._label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 200, 40),
            text=self._text(),
            manager=manager,
        )

        # re-render the label whenever the count changes; the subscription is
        # released automatically when this component is destroyed
        self.bind(count, self._refresh)

    def _text(self) -> str:
        return f"count: {self._count.value}"

    def _refresh(self) -> None:
        self._label.set_text(self._text())


class HomeScreen(axon.Screen[ScreenId]):
    def __init__(self, window_size: tuple[int, int]) -> None:
        manager = pygame_gui.UIManager(window_size)
        self._count = axon.Atom(0)
        super().__init__(manager, Counter(manager, self._count))

    @override
    def on_process_event(self, event: pygame.Event) -> ScreenId | None:
        # bump the atom on any key press; the Counter reacts on its own
        if event.type == pygame.KEYDOWN:
            self._count.value += 1
        return None


class DemoApp(axon.App[ScreenId]):
    pass


def main() -> None:
    window_size = (480, 240)
    app = DemoApp(
        app_name="Axon Counter",
        window_size=window_size,
        screens={ScreenId.HOME: HomeScreen(window_size)},
        initial_screen=ScreenId.HOME,
        fps=60,
    )
    app.run()  # blocks until the window is closed
