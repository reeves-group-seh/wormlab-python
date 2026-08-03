# std
import importlib.resources
from typing import TYPE_CHECKING, ClassVar, override

# pip
import pygame
import pygame_gui

# local
import axon
import axonkit
import shooter
from shooter.components import Feed, PanelHeading
from shooter.screens import ScreenId
from shooter.screens._events import CT_GO_HOME
from shooter.screens._util import create_manager

# relative
from ._layout import StartLayout

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppContext

__all__ = ["StartScreen"]


def _video_status_text(ctx: AppContext) -> str:
    """
    Check the currently opened camera's resolution against the expected
    resolution and describe the result as the "Video Status" field's text.
    """
    width = ctx.camera.width()
    height = ctx.camera.height()
    if width == ctx.cfg.EXPECTED_CAMERA_W and height == ctx.cfg.EXPECTED_CAMERA_H:
        return f"<b>Video Status</b>: OK ({width}x{height})"
    return (
        f"<b>Video Status</b>: WARN "
        f"(expected {ctx.cfg.EXPECTED_CAMERA_W}x{ctx.cfg.EXPECTED_CAMERA_H})"
    )


class StartScreen(axon.Screen[ScreenId]):
    # instance vars
    _ctx: AppContext
    _serial_port: axon.Atom[str]
    _camera_index: axon.Atom[int]
    _video_status: axon.Atom[str]

    def __init__(self, ctx: AppContext) -> None:
        # instance vars
        self._ctx = ctx
        self._serial_port = axon.Atom(ctx.arduino.ports()[0])
        self._camera_index = axon.Atom(ctx.cfg.DEFAULT_CAMERA_INDEX)

        # (try to) open default serial connection and camera
        self._ctx.arduino.open(self._serial_port.value)
        self._ctx.camera.open(self._camera_index.value)
        self._video_status = axon.Atom(_video_status_text(self._ctx))

        # create
        manager = create_manager(self._ctx)
        root = _StartScreenRoot(
            manager=manager,
            ctx=ctx,
            serial_port=self._serial_port,
            camera_index=self._camera_index,
            video_status=self._video_status,
        )

        # init parent
        super().__init__(manager, root)

    @override
    def on_process_event(self, event: pygame.Event) -> ScreenId | None:
        if event.type == CT_GO_HOME:
            # grab state values
            room_temp = self._ctx.state.room_temp.value
            room_humidity = self._ctx.state.room_humidity.value
            assert isinstance(room_temp, float)
            assert isinstance(room_humidity, float)

            # open data file
            self._ctx.data.open(
                data_dir=self._ctx.cfg.DATA_DIR,
                room_temp=room_temp,
                room_humidity=room_humidity,
            )
            return ScreenId.HOME

        return None


class _StartScreenRoot(axon.Component):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        ctx: AppContext,
        serial_port: axon.Atom[str],
        camera_index: axon.Atom[int],
        video_status: axon.Atom[str],
    ) -> None:
        # layout metrics
        lt = StartLayout(window_w=ctx.cfg.WINDOW_W, window_h=ctx.cfg.WINDOW_H)

        # background
        bg = axonkit.Background(
            manager=manager,
            size=ctx.cfg.WINDOW_SIZE,
        )

        # widths
        right_panel_w = lt.video_w
        left_panel_w = lt.window_w - (right_panel_w + lt.border)

        # heights
        bottom_panels_h = _FeedPanel.content_h(lt)
        top_panel_h = lt.window_h - (
            bottom_panels_h + lt.status_bar_h + (2 * lt.border)
        )
        info_panel_h = bottom_panels_h - (_ConfigPanel.content_h(lt) + lt.border)

        # status bar
        status_bar_panel_rect = pygame.Rect(0, 0, lt.window_w, lt.status_bar_h)
        status_bar_panel_rect.bottomleft = (0, 0)
        _StatusBarPanel(
            manager=manager,
            container=bg.element,
            rect=status_bar_panel_rect,
            anchors={"bottom": "bottom"},
        )

        # top panel
        top_panel = _TopPanel(
            manager=manager,
            container=bg.element,
            rect=(0, 0, lt.window_w, top_panel_h),
            lt=lt,
        )

        # info panel
        info_panel = _InfoPanel(
            manager=manager,
            container=bg.element,
            rect=(0, lt.border, left_panel_w, info_panel_h),
            lt=lt,
            ctx=ctx,
            video_status=video_status,
            anchors={"top": "top", "top_target": top_panel.element},
        )

        # config panel
        _ConfigPanel(
            manager=manager,
            container=bg.element,
            rect=(0, lt.border, left_panel_w, _ConfigPanel.content_h(lt)),
            lt=lt,
            ctx=ctx,
            serial_port=serial_port,
            camera_index=camera_index,
            video_status=video_status,
            anchors={"top": "top", "top_target": info_panel.element},
        )

        # video panel
        right_panel_rect = pygame.Rect(0, 0, right_panel_w, bottom_panels_h)
        right_panel_rect.topright = (0, lt.border)
        _FeedPanel(
            manager=manager,
            container=bg.element,
            rect=right_panel_rect,
            lt=lt,
            ctx=ctx,
            anchors={"top": "top", "top_target": top_panel.element, "right": "right"},
        )


class _TopPanel(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: StartLayout,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # root
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.DEFAULT,
        )

        # text
        ascii_art = (
            importlib.resources.files("shooter.resources") / "title.txt"
        ).read_text()
        axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(0, 0, panel.content_width(), panel.content_height()),
            text=f"{ascii_art}\n",
            obj_id="#ascii_art",
        )


class _InfoPanel(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: StartLayout,
        ctx: AppContext,
        video_status: axon.Atom[str],
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # root
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.DEFAULT,
        )

        # values
        content_w = panel.content_width() - (2 * lt.border_pad)
        inner_content_h = lt.stack(
            lt.label_h,  # version
            lt.label_label_pad_y,
            lt.label_h,  # video status
            lt.label_label_pad_y,
            lt.label_h,  # other
        )
        top_pad_y = (
            (panel.content_height() - (lt.panel_heading_h + inner_content_h)) // 2
        ) - 1

        # header
        heading = PanelHeading(
            manager=manager,
            container=panel.content,
            rect=(0, 0, rect.w, lt.panel_heading_h),
            text="INFO",
        )

        # version
        version_label = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, top_pad_y, content_w, lt.label_h),
            text=f"<b>Version</b>: {shooter.VERSION}",
            anchors={"top": "top", "top_target": heading.element},
        )

        # video status
        video_status_label = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_label_pad_y, content_w, lt.label_h),
            text=video_status,
            anchors={"top": "top", "top_target": version_label.element},
        )

        # other
        axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_label_pad_y, content_w, lt.label_h),
            text="<b>Serial Status</b>: ...",
            anchors={"top": "top", "top_target": video_status_label.element},
        )


class _ConfigPanel(axon.Widget):
    # instance vars
    _ctx: AppContext
    _serial_port: axon.Atom[str]
    _camera_index: axon.Atom[int]
    _video_status: axon.Atom[str]
    _start_btn: axonkit.Button

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: StartLayout,
        ctx: AppContext,
        serial_port: axon.Atom[str],
        camera_index: axon.Atom[int],
        video_status: axon.Atom[str],
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # instance vars
        self._ctx = ctx
        self._serial_port = serial_port
        self._camera_index = camera_index
        self._video_status = video_status

        # convert rect
        rect = axon.as_rect(rect)

        # root
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.DEFAULT,
        )

        # values
        content_w = panel.content_width() - (2 * lt.border_pad)

        # header
        heading = PanelHeading(
            manager=manager,
            container=panel.content,
            rect=(0, 0, rect.w, lt.panel_heading_h),
            text="CONFIG",
        )

        # serial
        serial_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.border_label_pad_y, content_w, lt.label_h),
            text="Serial",
            anchors={"top": "top", "top_target": heading.element},
        )
        serial_input = axonkit.CycleBox(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, content_w, lt.input_h),
            value=serial_port,
            options=ctx.arduino.ports(),
            anchors={"top": "top", "top_target": serial_label.element},
        )

        # camera
        camera_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.input_label_pad_y, content_w, lt.label_h),
            text="Camera",
            anchors={"top": "top", "top_target": serial_input.element},
        )
        camera_input = axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, content_w, lt.input_h),
            value=camera_index,
            parse=int,
            inc=lambda x: x + 1,
            dec=lambda x: max(0, x - 1),
            anchors={"top": "top", "top_target": camera_label.element},
        )

        # temp
        temp_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.input_label_pad_y, content_w, lt.label_h),
            text="TI Temperature (\u2103)",
            anchors={"top": "top", "top_target": camera_input.element},
        )
        temp_input = axonkit.InputStrict(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, content_w, lt.input_h),
            value=ctx.state.room_temp,
            parse=float,
            anchors={"top": "top", "top_target": temp_label.element},
        )

        # humidity
        humidity_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.input_label_pad_y, content_w, lt.label_h),
            text="TI Humidity (%)",
            anchors={"top": "top", "top_target": temp_input.element},
        )
        axonkit.InputStrict(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, content_w, lt.input_h),
            value=ctx.state.room_humidity,
            parse=float,
            anchors={"top": "top", "top_target": humidity_label.element},
        )

        # buttons
        start_btn_rect = pygame.Rect(0, 0, content_w, lt.input_h)
        start_btn_rect.bottomleft = (lt.border_pad, -lt.border_pad)
        self._start_btn = axonkit.Button(
            manager=manager,
            container=panel.content,
            rect=start_btn_rect,
            text="Start",
            on_click=self.handle_start_click,
            anchors={"bottom": "bottom"},
        )
        self._start_btn.disable()

        # reopen backends live when the port/camera selection changes
        self.bind(serial_port, self._on_serial_port_change)
        self.bind(camera_index, self._on_camera_index_change)

        # gate the start button on temp/humidity being filled in
        self.bind(ctx.state.room_temp, self._update_start_enabled)
        self.bind(ctx.state.room_humidity, self._update_start_enabled)
        self._update_start_enabled()

    @staticmethod
    def content_h(lt: StartLayout) -> int:
        return lt.stack(
            lt.panel_heading_h,  # header
            lt.border_label_pad_y,
            lt.label_h,  # serial label
            lt.label_input_pad_y,
            lt.input_h,  # serial input
            lt.input_label_pad_y,
            lt.label_h,  # camera label
            lt.label_input_pad_y,
            lt.input_h,  # camera input
            lt.input_label_pad_y,
            lt.label_h,  # temp label
            lt.label_input_pad_y,
            lt.input_h,  # temp input
            lt.input_label_pad_y,
            lt.label_h,  # humidity label
            lt.label_input_pad_y,
            lt.input_h,  # humitidy input
            lt.input_input_pad_y,
            lt.input_h,  # button
            lt.border_pad,
        )

    def handle_start_click(self) -> None:
        pygame.event.post(pygame.Event(CT_GO_HOME))

    def _on_serial_port_change(self) -> None:
        self._ctx.arduino.close()
        self._ctx.arduino.open(self._serial_port.value)

    def _on_camera_index_change(self) -> None:
        self._ctx.camera.close()
        self._ctx.camera.open(self._camera_index.value)
        self._video_status.value = _video_status_text(self._ctx)

    def _update_start_enabled(self) -> None:
        if (
            self._ctx.state.room_temp.value is not None
            and self._ctx.state.room_humidity.value is not None
        ):
            self._start_btn.enable()
        else:
            self._start_btn.disable()


class _FeedPanel(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: StartLayout,
        ctx: AppContext,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

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
            text="VIDEO FEED",
        )

        # video
        Feed(
            manager=manager,
            container=panel.content,
            rect=(0, 0, panel.content_width(), lt.video_h),
            camera=ctx.camera,
            show_grid=axon.Atom(False),
            anchors={"top": "top", "top_target": heading.element},
        )

    @staticmethod
    def content_h(lt: StartLayout) -> int:
        return StartLayout.stack(
            lt.panel_heading_h,
            lt.video_h,
        )


class _StatusBarPanel(axon.Widget):
    # class vars
    _TEXT_PAD_X: ClassVar[int] = 5

    # instance vars
    _left_text: axonkit.Text
    _right_text: axonkit.Text

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # root
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.DEFAULT,
            obj_id="#status_bar_panel",
        )

        # values
        text_w = panel.content_width() - (2 * _StatusBarPanel._TEXT_PAD_X)
        text_h = panel.content_height() - 2

        # left-aligned info
        self._left_text = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(_StatusBarPanel._TEXT_PAD_X, 0, text_w, text_h),
            text=f"<b>Framework</b>: axon-ui v{axon.VERSION}, axon-ui-kit v{axonkit.VERSION}",
            obj_id="#status_bar_text",
        )

        # right-aligned info
        right_text_rect = pygame.Rect(0, 0, text_w, text_h)
        right_text_rect.topright = (-_StatusBarPanel._TEXT_PAD_X, 0)
        self._right_text = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=right_text_rect,
            text="<i>developed with <3</i>",
            anchors={"right": "right"},
            obj_id="#status_bar_text_right",
        )
