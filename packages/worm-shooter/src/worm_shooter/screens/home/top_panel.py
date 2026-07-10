# std
from typing import ClassVar

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from worm_shooter.app.config import AppConfig
from worm_shooter.atom import Atom
from worm_shooter.components import (
    NO_MARGINS,
    Component,
    ControlLabelComponent,
    SpinBoxComponent,
    TextEntryLineComponent,
)


class TopPanelComponent(Component):
    # public class constants
    W: ClassVar[int] = 545
    H: ClassVar[int] = 220

    # instance vars
    _marker_pos: Atom[tuple[int, int]]
    _marker_x: Atom[int]
    _marker_y: Atom[int]

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        cfg: AppConfig,
        fire_duration: Atom[float],
        step_duration: Atom[float],
        move_speed: Atom[float],
        grid_size: Atom[int],
        marker_pos: Atom[tuple[int, int]],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._marker_pos = marker_pos
        self._marker_x = Atom(cfg.DEFAULT_MARKER_POS[0])
        self._marker_y = Atom(cfg.DEFAULT_MARKER_POS[1])

        # bind values
        self.bind(marker_pos, self._marker_pos_outer)
        self.bind(self._marker_x, self._marker_pos_inner)
        self.bind(self._marker_y, self._marker_pos_inner)

        # unpack values
        x, y = pos

        # create
        panel = UIPanel(
            relative_rect=(x, y, self.W, self.H),
            manager=manager,
            container=container,
            margins=NO_MARGINS,
        )

        # fire duration
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(10, 10),
            w=258,
            text="Fire Duration (ms)",
        )
        SpinBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 40),
            w=258,
            value=fire_duration,
            inc=lambda v: min(cfg.MAX_FIRE_DURATION, v + cfg.FIRE_DURATION_STEP),
            dec=lambda v: max(cfg.MIN_FIRE_DURATION, v - cfg.FIRE_DURATION_STEP),
            parse=float,
        )

        # step duration
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(10, 80),
            w=258,
            text="Move Duration (ms)",
        )
        SpinBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 110),
            w=258,
            value=step_duration,
            inc=lambda v: min(cfg.MAX_MOVE_DURATION, v + cfg.MOVE_DURATION_STEP),
            dec=lambda v: max(cfg.MIN_MOVE_DURATION, v - cfg.MOVE_DURATION_STEP),
            parse=float,
        )

        # move speed
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(10, 150),
            w=258,
            text="Move Speed (steps/s)",
        )
        SpinBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 180),
            w=258,
            value=move_speed,
            inc=lambda v: min(cfg.MAX_MOVE_SPEED, v + cfg.MOVE_SPEED_STEP),
            dec=lambda v: max(cfg.MIN_MOVE_SPEED, v - cfg.MOVE_SPEED_STEP),
            parse=float,
        )

        # grid size
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(277, 10),
            w=258,
            text="Grid Size",
        )
        SpinBoxComponent(
            manager=manager,
            container=panel,
            pos=(277, 40),
            w=258,
            value=grid_size,
            inc=lambda v: min(cfg.MAX_GRID_SIZE, v + 1),
            dec=lambda v: max(cfg.MIN_GRID_SIZE, v - 1),
            parse=int,
        )

        # marker position
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(277, 80),
            w=258,
            text="Marker Position",
        )
        TextEntryLineComponent(
            manager=manager,
            container=panel,
            pos=(277, 110),
            w=127,
            value=self._marker_x,
            parse=int,
            valid_class_id="@marker_pos_valid",
            invalid_class_id="@marker_pos_invalid",
        )
        TextEntryLineComponent(
            manager=manager,
            container=panel,
            pos=(408, 110),
            w=127,
            value=self._marker_y,
            parse=int,
            valid_class_id="@marker_pos_valid",
            invalid_class_id="@marker_pos_invalid",
        )

    def _marker_pos_outer(self) -> None:
        self._marker_x.value = self._marker_pos.value[0]
        self._marker_y.value = self._marker_pos.value[1]

    def _marker_pos_inner(self) -> None:
        self._marker_pos.value = (self._marker_x.value, self._marker_y.value)
