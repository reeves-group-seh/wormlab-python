# std
from collections.abc import Callable
from typing import ClassVar, override

# extern
import pygame
import pygame_gui

# local
import axon
from shooter.backend.camera import CameraBackend
from shooter.types import RadiusColor


class Feed(axon.Widget):
    """
    Feed of frames produced by a `CameraBackend`.

    Each frame is scaled to fit the widget's rect while preserving its aspect
    ratio, then centered. A feed whose aspect ratio does not match the widget's
    is letterboxed rather than stretched. The area left over around the frame is
    filled black.

    Two overlays can be drawn on top of the frame, each of which is independently
    optional:

    - **Grid**: A reference grid over the frame. Toggled by the `show_grid`
      atom.
    - **Marker**: Set of rings marking where the laser fires, with the ring
      named by `radius_color` drawn at full color and the rest dimmed. Toggled
      by the `show_marker` atom. This is only rendered when both `marker_pos`
      and `radius_color` are provided.

    Both toggles fall back to an atom the widget owns, so a control elsewhere in
    the tree can turn either overlay on and off.

    ## Mouse

    The feed reports the mouse in plane coordinates and takes no view on what
    that means: `hover_pos` follows the cursor, and `on_left_click` /
    `on_right_click` fire for clicks landing on the frame itself.

    ## Logical Plane

    `marker_pos` and the grid are in *plane* coordinates: a fixed logical space,
    720x480 units (this maps to the size of the video feed in pixels), that maps
    onto the frame however the frame happens to be scaled. Ring radii, by
    contrast, are in pixels, so they keep a constant on-screen size (this may be
    changed later).

    The cursor is reported in the same coordinates: a feed given a `hover_pos`
    atom keeps it set to the plane position the mouse is over, and to `None`
    whenever the mouse is off the frame.
    """

    # private class variables
    _BG_COLOR: ClassVar[pygame.Color] = pygame.Color.from_hex("#18181B")
    """
    Fill color of the area around the frame (the letterbox bars).
    """

    PLANE_W: ClassVar[int] = 720
    """
    Width of the logical plane the grid and marker are placed on.
    """

    PLANE_H: ClassVar[int] = 480
    """
    Height of the logical plane the grid and marker are placed on.
    """

    PLANE_CENTER: ClassVar[tuple[int, int]] = (PLANE_W // 2, PLANE_H // 2)
    """
    The center of the logical plane, in plane coordinates.
    """

    _GRID_COLOR: ClassVar[pygame.Color] = pygame.Color.from_hex("#571C3D")
    """
    Color of the grid lines.
    """

    _GRID_WIDTH: ClassVar[int] = 1
    """
    Thickness of the grid lines in pixels.
    """

    _GRID_STEP: ClassVar[int] = 60
    """
    Distance between two grid lines, in plane units.
    """

    _RINGS: ClassVar[list[tuple[RadiusColor, pygame.Color, int]]] = [
        (RadiusColor.RED, pygame.Color(255, 0, 0), 5),
        (RadiusColor.GREEN, pygame.Color(0, 255, 0), 25),
        (RadiusColor.BLUE, pygame.Color(0, 0, 255), 45),
        (RadiusColor.YELLOW, pygame.Color(255, 255, 0), 65),
    ]
    """
    The marker's rings, innermost first, as (color, draw color, radius in
    pixels).
    """

    _RING_WIDTH: ClassVar[int] = 1
    """
    Thickness of a ring in pixels. The innermost ring is drawn thicker, as it
    marks the marker's center.
    """

    _RING_WIDTH_INNER: ClassVar[int] = 2
    """
    Thickness of the innermost ring in pixels.
    """

    _RING_DIM: ClassVar[float] = 0.65
    """
    How far the rings that are not selected are faded towards the background,
    where 0.0 leaves them at full color and 1.0 makes them invisible.
    """

    # instance variables
    _camera: CameraBackend
    _show_grid: axon.Atom[bool]
    _marker_pos: axon.Atom[tuple[int, int]] | None
    _radius_color: axon.Atom[RadiusColor] | None
    _show_marker: axon.Atom[bool]
    _hover_pos: axon.Atom[tuple[int, int] | None] | None
    _on_left_click: Callable[[tuple[int, int]], None] | None
    _on_right_click: Callable[[tuple[int, int]], None] | None
    _frame_rect: pygame.Rect | None
    _size: tuple[int, int]
    _frame: pygame.Surface | None
    _dirty: bool

    # elements
    _image: pygame_gui.elements.UIImage

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        camera: CameraBackend,
        show_grid: axon.Atom[bool] | None = None,
        marker_pos: axon.Atom[tuple[int, int]] | None = None,
        radius_color: axon.Atom[RadiusColor] | None = None,
        show_marker: axon.Atom[bool] | None = None,
        hover_pos: axon.Atom[tuple[int, int] | None] | None = None,
        on_left_click: Callable[[tuple[int, int]], None] | None = None,
        on_right_click: Callable[[tuple[int, int]], None] | None = None,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        """
        Create a feed filling `rect`.

        :param manager: The `pygame_gui.UIManager` that owns this widget's
            elements.
        :param container: The container holding the feed, or `None` to place it
            at the root of the manager.
        :param rect: The feed's position and size, relative to `container`, or
            an anchored element's edge. Frames are letterboxed into it, so it
            does not need to match the camera's aspect ratio.
        :param camera: The backend to read frames from. It must be opened before
            the feed is updated; a closed backend that returns no frame leaves
            the feed blank.
        :param show_grid: Atom controlling whether the grid is drawn. Defaults to
            a new atom, held by the widget and initially `True`.
        :param marker_pos: The marker's position, in plane coordinates. Leave it
            out to build a feed with no marker at all.
        :param radius_color: The ring to draw at full color, the rest being
            dimmed. Leave it out to build a feed with no marker at all.
        :param show_marker: Atom controlling whether the marker is drawn.
            Defaults to a new atom, held by the
            widget and initially `True`. It has no effect unless both
            `marker_pos` and `radius_color` are given.
        :param hover_pos: Atom set to the plane position the mouse is over, and
            to `None` while it is off the frame. Leave it out to build a feed
            that does not track the mouse at all.
        :param on_left_click: Called with the plane position of a left click on
            the frame. Clicks on the letterbox bars are not reported.
        :param on_right_click: Called with the plane position of a right click
            on the frame. See `on_left_click`.
        :param anchors: A `pygame_gui` anchors mapping controlling how the feed
            is positioned. See `pygame_gui`'s documentation on how anchors work
            for more info.
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # set values
        self._camera = camera
        self._show_grid = axon.Atom(True) if show_grid is None else show_grid
        self._marker_pos = marker_pos
        self._radius_color = radius_color
        self._show_marker = axon.Atom(True) if show_marker is None else show_marker
        self._hover_pos = hover_pos
        self._on_left_click = on_left_click
        self._on_right_click = on_right_click
        self._frame_rect = None
        self._size = (rect.w, rect.h)
        self._frame = None
        self._dirty = False

        # blank (all letterbox) surface to show until the first frame arrives
        blank = pygame.Surface(self._size)
        blank.fill(self._BG_COLOR)

        # create
        self._image = pygame_gui.elements.UIImage(
            relative_rect=(0, 0, rect.w, rect.h),
            image_surface=blank,
            manager=manager,
            container=self.element,
        )

        # bind
        self.bind(self._show_grid, self._invalidate)
        self.bind(self._show_marker, self._invalidate)
        if self._marker_pos is not None:
            self.bind(self._marker_pos, self._invalidate)
        if self._radius_color is not None:
            self.bind(self._radius_color, self._invalidate)

    @property
    def show_grid(self) -> axon.Atom[bool]:
        """
        Atom controlling whether the grid is drawn over the frame.

        Set its value to turn the grid on and off. This is the atom passed to
        `__init__`, or the one the widget created if none was given.
        """
        return self._show_grid

    @property
    def show_marker(self) -> axon.Atom[bool]:
        """
        Atom controlling whether the marker is drawn over the frame.

        Set its value to turn the marker on and off. This is the atom passed to
        `__init__`, or the one the widget created if none was given. A feed built
        without `marker_pos` and `radius_color` has no marker to show, so this
        has no effect on it.
        """
        return self._show_marker

    @override
    def on_process_event(self, event: pygame.Event) -> None:
        """
        Track the mouse over the frame, and report clicks on it.

        A click is reported only when it lands on the frame itself, so one on
        the letterbox bars, or before the first frame arrives, does nothing.

        :param event: The `pygame` event to handle.
        """

        # the mouse moved, or left the window entirely
        if event.type == pygame.MOUSEMOTION:
            self._track_hover(event.pos)
            return
        if event.type == pygame.WINDOWLEAVE:
            self._set_hover(None)
            return

        # only the buttons someone is listening for
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        match event.button:
            case pygame.BUTTON_LEFT:
                callback = self._on_left_click
            case pygame.BUTTON_RIGHT:
                callback = self._on_right_click
            case _:
                return
        if callback is None:
            return

        # ignore clicks outside of the feed, and any before a frame is drawn
        abs_rect = self._image.get_abs_rect()
        if not abs_rect.collidepoint(event.pos) or self._frame_rect is None:
            return

        # report the plane position clicked, if the click was on the frame
        pos = self._px_to_plane(
            self._frame_rect,
            (event.pos[0] - abs_rect.x, event.pos[1] - abs_rect.y),
        )
        if pos is not None:
            callback(pos)

    @override
    def on_update(self, dt: float) -> None:
        """
        Read the next camera frame, if any, and redraw when something changed.

        :param dt: Seconds elapsed since the last frame.
        """

        # grab a frame, if one is available
        frame = self._camera.read_frame()
        if frame is not None:
            self._frame = pygame.surfarray.make_surface(frame)
            self._dirty = True

        # only redraw on a new frame, or a change to one of the overlays
        if self._dirty:
            self._render()
            self._dirty = False

    def _invalidate(self) -> None:
        self._dirty = True

    def _set_hover(self, pos: tuple[int, int] | None) -> None:
        """
        Publish a plane position to `hover_pos`, if the feed was given one.
        """
        if self._hover_pos is not None:
            self._hover_pos.value = pos

    def _track_hover(self, pos: tuple[float, float]) -> None:
        """
        Publish the plane position under `pos`, an absolute window position.
        """

        # nothing to report to, or nothing drawn to report a position over
        if self._hover_pos is None:
            return
        if self._frame_rect is None:
            self._set_hover(None)
            return

        # window pixels -> widget-local pixels -> the plane
        abs_rect = self._image.get_abs_rect()
        self._set_hover(
            self._px_to_plane(
                self._frame_rect,
                (pos[0] - abs_rect.x, pos[1] - abs_rect.y),
            )
        )

    def _render(self) -> None:
        # blank canvas, what is left of it shows as the letterbox bars
        canvas = pygame.Surface(self._size)
        canvas.fill(self._BG_COLOR)

        # nothing to draw on, and so nothing to click on or hover over either
        if self._frame is None:
            self._frame_rect = None
            self._set_hover(None)
            self._image.set_image(canvas)
            return

        # draw the frame, and the grid over it. the rect it landed in is kept
        # for the mouse, which is mapped against the frame as last drawn
        frame_rect = self._blit_fitted(canvas, self._frame)
        self._frame_rect = frame_rect
        if self._show_grid.value:
            self._draw_grid(canvas, frame_rect)

        # draw the marker, which needs both of its atoms to be of any use
        if (
            self._marker_pos is not None
            and self._radius_color is not None
            and self._show_marker.value
        ):
            marker_px = self._plane_to_px(frame_rect, self._marker_pos.value)
            self._draw_marker(canvas, marker_px, self._radius_color.value)

        # hand the canvas over to the element
        self._image.set_image(canvas)

    def _blit_fitted(
        self,
        canvas: pygame.Surface,
        frame: pygame.Surface,
    ) -> pygame.Rect:
        """
        Blit `frame` onto `canvas`, scaled to fit while preserving its aspect
        ratio and centered, and return the rect it ended up occupying.
        """

        # sizes
        box_w, box_h = self._size
        src_w, src_h = frame.get_size()

        # scale by the limiting dimension so the whole frame fits in the box
        scale = min(box_w / src_w, box_h / src_h)
        new_w = max(1, round(src_w * scale))
        new_h = max(1, round(src_h * scale))

        # center what is left over becomes the letterbox bars
        frame_rect = pygame.Rect(
            (box_w - new_w) // 2,
            (box_h - new_h) // 2,
            new_w,
            new_h,
        )
        canvas.blit(pygame.transform.scale(frame, (new_w, new_h)), frame_rect)
        return frame_rect

    def _plane_to_px(
        self,
        frame_rect: pygame.Rect,
        pos: tuple[int, int],
    ) -> tuple[int, int]:
        """
        Convert a plane position to a pixel position within `frame_rect`.
        """
        plane_x, plane_y = pos
        return (
            frame_rect.left + round((plane_x / self.PLANE_W) * frame_rect.width),
            frame_rect.top + round((plane_y / self.PLANE_H) * frame_rect.height),
        )

    def _px_to_plane(
        self,
        frame_rect: pygame.Rect,
        pos: tuple[float, float],
    ) -> tuple[int, int] | None:
        """
        Convert a pixel position within the widget to a plane position, or
        `None` when it lands outside `frame_rect`, on the letterbox bars.
        """

        # the bars are not part of the plane, so there is no position to give
        if not frame_rect.collidepoint(pos):
            return None

        # scale into the plane, relative to the frame's top left corner
        x, y = pos
        return (
            round(((x - frame_rect.left) / frame_rect.width) * self.PLANE_W),
            round(((y - frame_rect.top) / frame_rect.height) * self.PLANE_H),
        )

    def _draw_grid(self, canvas: pygame.Surface, frame_rect: pygame.Rect) -> None:
        # vertical lines, from the plane's left edge
        for plane_x in range(0, self.PLANE_W + 1, self._GRID_STEP):
            x = min(
                frame_rect.left + round((plane_x / self.PLANE_W) * frame_rect.width),
                frame_rect.right - 1,
            )
            pygame.draw.line(
                canvas,
                self._GRID_COLOR,
                (x, frame_rect.top),
                (x, frame_rect.bottom - 1),
                self._GRID_WIDTH,
            )

        # horizontal lines, from the plane's top edge
        for plane_y in range(0, self.PLANE_H + 1, self._GRID_STEP):
            y = min(
                frame_rect.top + round((plane_y / self.PLANE_H) * frame_rect.height),
                frame_rect.bottom - 1,
            )
            pygame.draw.line(
                canvas,
                self._GRID_COLOR,
                (frame_rect.left, y),
                (frame_rect.right - 1, y),
                self._GRID_WIDTH,
            )

    def _draw_marker(
        self,
        canvas: pygame.Surface,
        marker_px: tuple[int, int],
        selected: RadiusColor,
    ) -> None:
        # the selected ring keeps its color, the rest fade into the background,
        # innermost first, drawn thicker as it marks the center
        for idx, (color, draw_color, radius) in enumerate(self._RINGS):
            shade = (
                draw_color
                if color == selected
                else draw_color.lerp(self._BG_COLOR, self._RING_DIM)
            )
            pygame.draw.circle(
                canvas,
                shade,
                marker_px,
                radius,
                self._RING_WIDTH_INNER if idx == 0 else self._RING_WIDTH,
            )
