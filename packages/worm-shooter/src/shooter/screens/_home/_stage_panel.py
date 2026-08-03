# std
from typing import TYPE_CHECKING

# extern
import pygame
import pygame_gui

# local
import axon
import axonkit
from shooter.components import PanelHeading

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppConfig


class StagePanel(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: HomeLayout,
        cfg: AppConfig,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # width
        content_w = rect.w - (2 * lt.border_pad)
        column_w = (content_w - lt.column_pad_x) // 2

        # panel
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.w, rect.h),
            margins=axonkit.MarginOption.DEFAULT,
        )

        # header
        heading = PanelHeading(
            manager=manager,
            container=panel.content,
            rect=(0, 0, panel.content_width(), lt.panel_heading_h),
            text="LASER & STAGE",
        )

        # left column
        md_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.border_label_pad_y, column_w, lt.label_h),
            text="Move Duration (ms)",
            anchors={"top": "top", "top_target": heading.element},
        )
        axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, column_w, lt.input_h),
            value=state.step_duration,
            inc=lambda x: min(cfg.MAX_MOVE_DURATION, x + cfg.MOVE_DURATION_STEP),
            dec=lambda x: max(cfg.MIN_MOVE_DURATION, x - cfg.MOVE_DURATION_STEP),
            parse=float,
            anchors={"top": "top", "top_target": md_label.element},
        )
        ms_input_rect = pygame.Rect(0, 0, column_w, lt.input_h)
        ms_input_rect.bottomleft = (lt.border_pad, -lt.border_pad)
        ms_input = axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=ms_input_rect,
            value=state.move_speed,
            inc=lambda x: min(cfg.MAX_MOVE_SPEED, x + cfg.MOVE_SPEED_STEP),
            dec=lambda x: max(cfg.MIN_MOVE_SPEED, x - cfg.MOVE_SPEED_STEP),
            parse=float,
            anchors={"bottom": "bottom"},
        )
        ms_label_rect = pygame.Rect(0, 0, column_w, lt.label_h)
        ms_label_rect.bottomleft = (lt.border_pad, -lt.label_input_pad_y)
        axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=ms_label_rect,
            text="Move Speed (steps/s)",
            anchors={"bottom": "bottom", "bottom_target": ms_input.element},
        )

        # right column
        fd_label_rect = pygame.Rect(0, 0, column_w, lt.label_h)
        fd_label_rect.topright = (-lt.border_pad, lt.border_label_pad_y)
        fd_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=fd_label_rect,
            text="Fire Duration (ms)",
            anchors={"top": "top", "top_target": heading.element, "right": "right"},
        )
        fd_input_rect = pygame.Rect(0, 0, column_w, lt.input_h)
        fd_input_rect.topright = (-lt.border_pad, lt.label_input_pad_y)
        axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=fd_input_rect,
            value=state.fire_duration,
            inc=lambda x: min(cfg.MAX_FIRE_DURATION, x + cfg.FIRE_DURATION_STEP),
            dec=lambda x: max(cfg.MIN_FIRE_DURATION, x - cfg.FIRE_DURATION_STEP),
            parse=float,
            anchors={"top": "top", "top_target": fd_label.element, "right": "right"},
        )
        gs_input_rect = pygame.Rect(0, 0, column_w, lt.input_h)
        gs_input_rect.bottomright = (-lt.border_pad, -lt.border_pad)
        gs_input = axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=gs_input_rect,
            value=state.grid_size,
            inc=lambda x: min(cfg.MAX_GRID_SIZE, x + 1),
            dec=lambda x: max(cfg.MIN_GRID_SIZE, x - 1),
            parse=int,
            anchors={"bottom": "bottom", "right": "right"},
        )
        gs_label_rect = pygame.Rect(0, 0, column_w, lt.label_h)
        gs_label_rect.bottomright = (-lt.border_pad, -lt.label_input_pad_y)
        axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=gs_label_rect,
            text="Grid Size",
            anchors={
                "bottom": "bottom",
                "bottom_target": gs_input.element,
                "right": "right",
            },
        )
