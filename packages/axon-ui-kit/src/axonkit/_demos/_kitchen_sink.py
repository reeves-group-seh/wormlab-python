# std
import enum
from enum import Enum
from typing import Any, ClassVar

# extern
import pygame
import pygame_gui

# local
import axon
import axonkit

# WINDOW_SIZE = (720, 480)


class _ScreenID(Enum):
    HOME = enum.auto()


class KitchenSinkApp(axon.App[_ScreenID]):
    # class constants
    _NAME: ClassVar[str] = "Axon UI Component Kit"
    _WINDOW_SIZE: ClassVar[tuple[int, int]] = (720, 480)
    _FPS: ClassVar[int] = 60

    def __init__(self) -> None:
        super().__init__(
            app_name=self._NAME,
            window_size=self._WINDOW_SIZE,
            screen_factories={
                _ScreenID.HOME: lambda: _HomeScreen(self._WINDOW_SIZE),
            },
            initial_screen=_ScreenID.HOME,
            fps=self._FPS,
        )


class _HomeScreen(axon.Screen[_ScreenID]):
    def __init__(self, window_size: tuple[int, int]) -> None:
        # create
        manager = pygame_gui.UIManager(
            window_size,
            axonkit.DEFAULT_THEME,
        )
        root = _HomeRoot(manager, window_size)

        # super
        super().__init__(manager, root)


class _HomeRoot(axon.Component):
    # instance vars
    _txt_value: axon.Atom[str]
    _float_value: axon.Atom[float]
    _int_value: axon.Atom[int | None]
    _clicks: axon.Atom[int]

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
    ) -> None:
        # consts
        OUTER_PADDING = 20
        INNER_PADDING = 10
        PANEL_WIDTH = (window_size[0] - (3 * OUTER_PADDING)) / 2
        PANEL_HEIGHT = window_size[1] - (2 * OUTER_PADDING)
        CONTENT_WIDTH = PANEL_WIDTH - (2 * INNER_PADDING)

        # create state
        self._txt_value = axon.Atom("text")
        self._float_value = axon.Atom(22.0)
        self._int_value = axon.Atom(None)
        self._clicks = axon.Atom(0)

        # make background
        bg = axonkit.Background(manager=manager, size=window_size)

        #
        # left panel
        #

        l_panel = axonkit.Panel(
            manager=manager,
            container=bg.element,
            rect=pygame.Rect(OUTER_PADDING, OUTER_PADDING, PANEL_WIDTH, PANEL_HEIGHT),
        )

        # top-down
        l_label1 = axonkit.Label(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, INNER_PADDING, CONTENT_WIDTH, 20),
            text="Text Content",
        )
        l_text1 = axonkit.Text(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 2, CONTENT_WIDTH, 42),
            text="Lorem ipsum dolor sit amet, <a>consectetur</a> adipiscing elit. Morbi ut porta odio.",
            anchors={"top": "top", "top_target": l_label1.element},
        )
        l_label2 = axonkit.Label(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Text Input",
            anchors={"top": "top", "top_target": l_text1.element},
        )
        l_input2 = axonkit.Input(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=self._txt_value,
            parse=str,
            anchors={"top": "top", "top_target": l_label2.element},
        )
        l_label3 = axonkit.Label(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Float Input (lazy)",
            anchors={"top": "top", "top_target": l_input2.element},
        )
        l_input3 = axonkit.Input(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=self._float_value,
            parse=float,
            anchors={"top": "top", "top_target": l_label3.element},
        )
        l_label4 = axonkit.Label(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Integer Input (strict)",
            anchors={"top": "top", "top_target": l_input3.element},
        )
        l_input4 = axonkit.InputStrict(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=self._int_value,
            parse=int,
            anchors={"top": "top", "top_target": l_label4.element},
        )
        self._l_text5 = axonkit.Text(
            manager=manager,
            container=l_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 86),
            text=self._values_text(),
            anchors={"top": "top", "top_target": l_input4.element},
        )

        # bottom-up
        l_button_7_rect = pygame.Rect(INNER_PADDING, 0, CONTENT_WIDTH, 28)
        l_button_7_rect.bottom = -INNER_PADDING
        l_button_7 = axonkit.Button(
            manager=manager,
            container=l_panel.element,
            rect=l_button_7_rect,
            text="Increment",
            on_click=self._on_inc_click,
            anchors={"bottom": "bottom"},
        )
        l_button_6_rect = pygame.Rect(INNER_PADDING, 0, CONTENT_WIDTH, 28)
        l_button_6_rect.bottom = -10
        axonkit.Button(
            manager=manager,
            container=l_panel.element,
            rect=l_button_6_rect,
            text="Reset",
            on_click=self._on_reset_click,
            anchors={"bottom": "bottom", "bottom_target": l_button_7.element},
        )

        #
        # right panel
        #

        r_panel = axonkit.Panel(
            manager=manager,
            container=bg.element,
            rect=pygame.Rect(OUTER_PADDING, OUTER_PADDING, PANEL_WIDTH, PANEL_HEIGHT),
            anchors={"left": "left", "left_target": l_panel.element},
        )

        # top-down
        r_label1 = axonkit.Label(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, INNER_PADDING, CONTENT_WIDTH, 20),
            text="Disabled Input",
        )
        r_input1 = axonkit.Input(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=axon.Atom("disabled"),
            parse=str,
            anchors={"top": "top", "top_target": r_label1.element},
        )
        r_input1.disable()
        r_label2 = axonkit.Label(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Disabled Button",
            anchors={"top": "top", "top_target": r_input1.element},
        )
        r_button2 = axonkit.Button(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            text="Submit",
            anchors={"top": "top", "top_target": r_label2.element},
        )
        r_button2.disable()
        r_label3 = axonkit.Label(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Integer Spin Box (lazy)",
            anchors={"top": "top", "top_target": r_button2.element},
        )
        r_spin_box3 = axonkit.SpinBox(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=axon.Atom(22),
            inc=lambda x: x + 1,
            dec=lambda x: x - 1,
            parse=int,
            anchors={"top": "top", "top_target": r_label3.element},
        )
        r_label4 = axonkit.Label(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Float Spin Box (strict)",
            anchors={"top": "top", "top_target": r_spin_box3.element},
        )
        r_spin_box4 = axonkit.SpinBoxStrict(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=axon.Atom(22.2),
            inc=lambda x: x + 1.0,
            dec=lambda x: x - 1.0,
            parse=float,
            anchors={"top": "top", "top_target": r_label4.element},
        )
        r_label5 = axonkit.Label(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 10, CONTENT_WIDTH, 20),
            text="Cycle Box",
            anchors={"top": "top", "top_target": r_spin_box4.element},
        )
        axonkit.CycleBox(
            manager=manager,
            container=r_panel.element,
            rect=pygame.Rect(INNER_PADDING, 5, CONTENT_WIDTH, 28),
            value=axon.Atom("red"),
            options=["red", "green", "blue"],
            anchors={"top": "top", "top_target": r_label5.element},
        )

        #
        # bind
        #

        self.bind(self._txt_value, self._render)
        self.bind(self._float_value, self._render)
        self.bind(self._int_value, self._render)
        self.bind(self._clicks, self._render)

    def _on_reset_click(self) -> None:
        self._clicks.value = 0

    def _on_inc_click(self) -> None:
        self._clicks.value += 1

    def _values_text(self) -> str:
        values: dict[str, Any] = {
            "Text": self._txt_value.value,
            "Float": self._float_value.value,
            "Integer": self._int_value.value,
            "Clicks": self._clicks.value,
        }
        return "<br/>".join(f"<b>{key}</b>: {value}" for key, value in values.items())

    def _render(self) -> None:
        self._l_text5.set_text(self._values_text())
