# std
import dataclasses
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

# pip
import pygame
from pygame_gui import PackageResource

# local
import worm_shooter.resources
from worm_shooter.types import FilterNumber, KeyMapAction, RadiusColor


@dataclass(kw_only=True)
class AppConfig:
    """
    Configuration defined at application start and not changed throughout the
    app lifecycle.
    """

    DEFAULT_MARKER_POS: tuple[int, int] = (180, 300)
    """
    Position of the the marker relative to the video grid.
    """

    DATA_DIR: Path = dataclasses.field(
        default_factory=lambda: Path("C:/Users/reeve/Documents/WormData")
    )
    """
    Directory where CSV data files are created.
    """

    FPS: int = 60
    """
    Max number of frames per second to render at.
    """

    WINDOW_W: int = 1000
    """
    Width of the display.
    """

    WINDOW_H: int = 650
    """
    Height of the display.
    """

    THEME_FILE: PackageResource = dataclasses.field(
        default_factory=lambda: PackageResource(
            worm_shooter.resources.__name__, "theme.json"
        )
    )
    """
    The location of the main `theme.json` file.
    """

    KEYMAP: dict[int, KeyMapAction] = dataclasses.field(
        default_factory=lambda: {
            # steps
            pygame.K_h: KeyMapAction.STEP_LEFT,
            pygame.K_k: KeyMapAction.STEP_RIGHT,
            pygame.K_u: KeyMapAction.STEP_UP,
            pygame.K_j: KeyMapAction.STEP_DOWN,
            # movement
            pygame.K_LEFT: KeyMapAction.MOVE_LEFT,
            pygame.K_RIGHT: KeyMapAction.MOVE_RIGHT,
            pygame.K_UP: KeyMapAction.MOVE_UP,
            pygame.K_DOWN: KeyMapAction.MOVE_DOWN,
            # other
            pygame.K_f: KeyMapAction.FIRE,
            pygame.K_d: KeyMapAction.DESTROY,
            pygame.K_m: KeyMapAction.GRID,
            pygame.K_p: KeyMapAction.SKIP_DATA,
        }
    )
    """
    Main application keymap.
    """

    COUNTDOWN_LENGTH: int = 15
    """
    Number of seconds for fire countdown.
    """

    # start screen defaults

    DEFAULT_CAMERA_INDEX: int = 1
    """
    OpenCV video capture camera index.
    """

    # data defaults

    DEFAULT_RADIUS_COLOR: RadiusColor = RadiusColor.YELLOW
    """
    Default selected radius color.
    """

    DEFAULT_FILTER_NUMBER: FilterNumber = FilterNumber.FOUR
    """
    Default selected filter number.
    """

    DEFAULT_WORM_STRAIN: str = "N2"
    """
    Default worm strain.
    """

    # movement speed

    DEFAULT_MOVE_SPEED: float = 100.0
    """
    Default stage movement speed in steps per second.
    """

    MIN_MOVE_SPEED: float = 10.0
    """
    Minimum stage movement speed in steps per second.
    """

    MAX_MOVE_SPEED: float = 1000.0
    """
    Maximum stage movement speed in steps per second.
    """

    MOVE_SPEED_STEP: float = 10.0
    """
    Value to increment and decrement movement speed by in steps per second.
    """

    # move duration

    DEFAULT_MOVE_DURATION: float = 100.0
    """
    Default duration of stage movement commands in milliseconds.
    """

    MIN_MOVE_DURATION: float = 1.0
    """
    Mimimum duration of stage movement commands in milliseconds.
    """

    MAX_MOVE_DURATION: float = 5000.0
    """
    Maximum duration of stage movement commands in milliseconds.
    """

    MOVE_DURATION_STEP: float = 10.0
    """
    Value to increment and decrement duration of movement commands by in
    milliseconds.
    """

    # fire duration

    DEFAULT_FIRE_DURATION: float = 200.0
    """
    Default duration of laser fire commands in milliseconds.
    """

    MIN_FIRE_DURATION: float = 1.0
    """
    Mimimum duration of laser fire commands in milliseconds.
    """

    MAX_FIRE_DURATION: float = 10000.0
    """
    Maximum duration of laser fire commands in milliseconds.
    """

    FIRE_DURATION_STEP: float = 10.0
    """
    Value to increment and decrement duration of laser fire commands by in
    milliseconds.
    """

    DESTROY_FIRE_DURATION: float = 200.0
    """
    Duration of fire command when using "destroy".
    """

    # grid size

    DEFAULT_GRID_SIZE: int = 3
    """
    Default size of the square test grid.
    """

    MIN_GRID_SIZE: int = 1
    """
    Minumum size of the square test grid.
    """

    MAX_GRID_SIZE: int = 20
    """
    Maximum size of the square test grid.
    """

    # arduino

    SERIAL_BAUDRATE: int = 115200
    """
    Baude rate to communicate with the arduino at.
    """

    SERIAL_TIMEOUT: float = 0.1
    """
    Time in seconds to timeout the connection to the arduino.
    """

    SERIAL_SLEEP_FACTOR: float = 1.1
    """
    A factor determining how long to wait between writes to the arduino. A value
    of 1.0 indicates the program will wait for exactly the theroretical
    execution time of a command before sending another. A value of 2.0 indicates
    the program will wait for double this theroretical execution time, 0.5 will
    wait half, etc. To be safe, this value should be set to a value > 1.0.
    """

    # derived fields

    WINDOW_SIZE: tuple[int, int] = dataclasses.field(init=False)
    """
    Width and height of the window.
    """

    DATA_FILE: Path = dataclasses.field(init=False)
    """
    Path of the CSV data file to create & write to.
    """

    def __post_init__(self) -> None:
        # derived fields
        self.DATA_FILE = (
            self.DATA_DIR / f"{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}_data.csv"
        )
        self.WINDOW_SIZE = (self.WINDOW_W, self.WINDOW_H)
