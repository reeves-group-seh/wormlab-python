# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.components import NO_MARGINS, Component
from stage_ui.components.control_label import ControlLabelComponent
from stage_ui.components.spin_box import SpinBoxComponent
from stage_ui.config import Config


class TopPanelComponent(Component):
    # constants
    W: int = 545
    H: int = 220

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        cfg: Config,
        fire_duration: Atom[float],
        step_duration: Atom[float],
        move_speed: Atom[float],
        grid_size: Atom[int],
    ) -> None:
        # init parent
        super().__init__()

        # unpack values
        x, y = pos

        # create
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                container=container,
                margins=NO_MARGINS,
            )
        )

        # fire duration
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 10),
                w=258,
                text="Fire Duration (ms)",
            )
        )
        self.track(
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
        )

        # step duration
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 80),
                w=258,
                text="Step Duration (ms)",
            )
        )
        self.track(
            SpinBoxComponent(
                manager=manager,
                container=panel,
                pos=(10, 110),
                w=258,
                value=step_duration,
                inc=lambda v: min(cfg.MAX_STEP_DURATION, v + cfg.STEP_DURATION_STEP),
                dec=lambda v: max(cfg.MIN_STEP_DURATION, v - cfg.STEP_DURATION_STEP),
                parse=float,
            )
        )

        # move speed
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 150),
                w=258,
                text="Move Speed (steps/s)",
            )
        )
        self.track(
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
        )

        # grid size
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(277, 10),
                w=258,
                text="Grid Size",
            )
        )
        self.track(
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
        )
