# std
import datetime as dt
from pathlib import Path

# pip
import pygame
from pygame_gui import PackageResource

# local
from stage_ui.types import FilterNumber, KeyMapAction, RadiusColor


class Config:
    """
    Configuration defined at application start and not changed throughout the
    app lifecycle.
    """

    def __init__(
        self,
        data_dir: Path,
        testing: bool = False,
        camera_index: int | None = None,
    ) -> None:
        self.MARKER_POS: tuple[float, float] = (200.0, 311.0)
        """
        Position of the the marker relative to the video grid.
        """

        self.TESTING: bool = testing
        """
        Whether the app should be run in "testing" mode.
        """

        self.APP_NAME: str = "Stage Controller"
        """
        Application name.
        """

        self.DATA_FILE: Path = (
            data_dir / f"{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}_data.csv"
        )
        """
        Name of the CSV datafile to create & write to.
        """

        self.FPS: int = 60
        """
        Max number of frames per second to render at.
        """

        self.CAMERA_INDEX: int = camera_index if camera_index is not None else 3
        """
        OpenCV video capture camera index.
        """

        self.WINDOW_W: int = 1000
        """
        Width of the display.
        """

        self.WINDOW_H: int = 650
        """
        Height of the display.
        """

        self.PACKAGE_NAME: str = "stage_ui"
        """
        Name of this package.
        """

        self.THEME_FILE: PackageResource = PackageResource(
            f"{self.PACKAGE_NAME}.resources", "theme.json"
        )
        """
        The location of the main `theme.json` file.
        """

        #
        # movement speed
        #

        self.MOVE_SPEED_STEP: float = 10.0
        """
        Value to increment and decrement speed by in steps per second.
        """

        self.MIN_MOVE_SPEED: float = 10.0
        """
        Minimum stage movement speed in steps per second.
        """

        self.MAX_MOVE_SPEED: float = 1000.0
        """
        Maximum stage movement speed in steps per second.
        """

        self.DEFAULT_MOVE_SPEED: float = 100.0
        """
        Default stage movement speed in steps per second.
        """

        #
        # step duration
        #

        self.STEP_DURATION_STEP: float = 10.0
        """
        Value to increment and decrement step duration by in milliseconds.
        """

        self.MIN_STEP_DURATION: float = 1.0
        """
        Mimimum stage step duration in milliseconds.
        """

        self.MAX_STEP_DURATION: float = 5000.0
        """
        Maximum stage step duration in milliseconds.
        """

        self.DEFAULT_STEP_DURATION: float = 100.0
        """
        Default stage step duration in milliseconds.
        """

        #
        # fire duration
        #

        self.FIRE_DURATION_STEP: float = 10.0
        """
        Value to increment and decrement fire duration by in milliseconds.
        """

        self.MIN_FIRE_DURATION: float = 1.0
        """
        Mimimum laser fire duration in milliseconds.
        """

        self.MAX_FIRE_DURATION: float = 10000.0
        """
        Maximum laser fire duration in milliseconds.
        """

        self.DEFAULT_FIRE_DURATION: float = 200.0
        """
        Default laser fire duration in milliseconds.
        """

        #
        # grid
        #

        self.MIN_GRID_SIZE: int = 1
        """
        Minumum size of the square test grid.
        """

        self.MAX_GRID_SIZE: int = 20
        """
        Maximum size of the square test grid.
        """

        self.DEFAULT_GRID_SIZE: int = 3
        """
        Default size of the square test grid.
        """

        self.DEFAULT_GRID_SPEED: float = 100.0
        """
        Default speed when running the step-and-shoot.
        """

        self.DEFAULT_GRID_MOVE_DURATION: float = 10.0
        """
        Default duration of moves during step-and-shoot.
        """

        self.DEFAULT_GRID_FIRE_DURATION: float = 200.0
        """
        Default duration of fires during step-and-shoot.
        """

        #
        # other defaults
        #

        self.DEFAULT_STRAIN: str = "N2"
        """
        Default worm strain.
        """

        self.DEFAULT_FILTER_NUMBER: FilterNumber = FilterNumber.FOUR
        """
        Default selected filter number.
        """

        self.DEFAULT_RADIUS_COLOR: RadiusColor = RadiusColor.YELLOW
        """
        Default selected radius color.
        """

        #
        # serial
        #

        self.SERIAL_PORT: str = "COM4"
        """
        Port to connect to the arduino on.
        """

        self.SERIAL_BAUDRATE: int = 115200
        """
        Baude rate to communicate with arduino at.
        """

        self.SERIAL_TIMEOUT: float = 0.1
        """
        Time in seconds to timeout the connection to the arduino.
        """

        self.SERIAL_SLEEP_FACTOR: float = 1.5
        """
        A factor determining how long to wait between writes to the arduino. A value
        of 1.0 indicates the program will wait for exactly the theroretical
        execution time of a command before sending another. A value of 2.0 indicates
        the program will wait for double this theroretical execution time, 0.5 will
        wait half, etc. To be safe, this value should be set to a value > 1.0.
        """

        #
        # keymaps
        #

        self.KEYMAP: dict[int, KeyMapAction] = {
            # steps
            pygame.K_h: KeyMapAction.STEP_LEFT,
            pygame.K_k: KeyMapAction.STEP_RIGHT,
            pygame.K_u: KeyMapAction.STEP_UP,
            pygame.K_j: KeyMapAction.STEP_DOWN,
            # movement
            pygame.K_LEFT: KeyMapAction.MOVE_LEFT,
            pygame.K_RIGHT: KeyMapAction.MOVE_RIGHT,
            pygame.K_UP: KeyMapAction.MOVE_UP,
            pygame.K_DOWN: KeyMapAction.MOVE_UP,
            # speed
            pygame.K_w: KeyMapAction.INC_SPEED,
            pygame.K_s: KeyMapAction.DEC_SPEED,
            # other
            pygame.K_ESCAPE: KeyMapAction.QUIT,
            pygame.K_f: KeyMapAction.FIRE,
            pygame.K_d: KeyMapAction.DESTROY,
            pygame.K_m: KeyMapAction.GRID,
            pygame.K_p: KeyMapAction.SKIP_DATA,
        }
        """
        Main application keymap.
        """

    #
    # derived helper values
    #

    @property
    def WINDOW_SIZE(self) -> tuple[int, int]:
        return (self.WINDOW_W, self.WINDOW_H)
