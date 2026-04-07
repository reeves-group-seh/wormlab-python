# item imports
from dataclasses import dataclass
from pygame import Clock
from pygame_gui import PackageResource, UIManager

# local item imports
from app_config import AppConfig
from app_types import FilterNumber, RadiusColor
from manager_data import DataManager
from manager_serial import SerialManager
from manager_video import VideoManager


@dataclass(kw_only=True)
class AppState:
    """
    All mutable application state.
    """

    running: bool = True
    """
    Whether the application is currently running.
    """

    time_delta: float = 0.0
    """
    Time in seconds since the last frame.
    """

    clock: Clock
    """
    Clock used in the render loop.
    """

    #
    # startup values
    #

    room_temp: float | None = None
    """
    Temperature of the room in degrees celsius.
    """

    #
    # arduino command-related values
    #

    speed: float
    """
    Speed to move the stage at in steps per second.
    """

    move_duration: float
    """
    Duration of move commands in milliseconds.
    """

    fire_duration: float
    """
    Duration of fire commands in nulliseconds.
    """

    grid_size: int
    """
    Size of the NxN grid for the step-and-shoot functionality.
    """

    #
    # data entry values
    #

    filter_num: FilterNumber
    """
    Number of the filter being used.
    """

    radius_color: RadiusColor
    """
    Name of the selected radius color.
    """

    worm_strain: str | None = None
    """
    Name of the worm strain to record with fires.
    """

    worm_id: int = 1
    """
    ID (or index) of the currenly focused worm.
    """

    #
    # fire-related values
    #

    fire_count: int = 0
    """
    Number of fires on the current worm (fires since `worm_id` has changed).
    """

    unrecorded_fire: FireInstance | None = None
    """
    Info about a fire that has yet to be recorded.
    """

    #
    # managers
    #

    data_man: DataManager
    """
    Datafile create and update logic.
    """

    serial_man: SerialManager
    """
    Connection to the arduino.
    """

    video_man: VideoManager
    """
    Frame capture and video-related state.
    """

    ui_man: UIManager
    """
    Pygame GUI manager.
    """

    #
    # private values
    #

    _cfg: AppConfig

    #
    # dynamic properties
    #

    @property
    def data_needed(self) -> bool:
        """
        Whether data needs to be recorded.
        """
        return self.unrecorded_fire is not None

    #
    # methods
    #

    @staticmethod
    def new(cfg: AppConfig) -> AppState:
        return AppState(
            clock=Clock(),
            speed=cfg.DEFAULT_SPEED,
            move_duration=cfg.DEFAULT_MOVE_DURATION,
            fire_duration=cfg.DEFAULT_FIRE_DURATION,
            grid_size=cfg.DEFAULT_GRID_SIZE,
            filter_num=cfg.DEFAULT_FILTER_NUMBER,
            radius_color=cfg.DEFAULT_RADIUS_COLOR,
            data_man=DataManager.new(cfg.DATA_FILE),
            serial_man=SerialManager.new(
                cfg.SERIAL_PORT,
                cfg.SERIAL_BAUDRATE,
                cfg.SERIAL_TIMEOUT,
                cfg.SERIAL_SLEEP_FACTOR,
                cfg.DEFAULT_GRID_SPEED,
                cfg.DEFAULT_GRID_MOVE_DURATION,
                cfg.DEFAULT_GRID_FIRE_DURATION,
            ),
            video_man=VideoManager.new(cfg.CAMERA_INDEX),
            ui_man=UIManager(
                (cfg.WINDOW_W, cfg.WINDOW_H),
                PackageResource(f"{cfg.PACKAGE_NAME}.resources", "theme.json"),
            ),
            _cfg=cfg,
        )

    def speed_increment(self) -> None:
        """
        Increment the value of movement speed by a standard value.
        """
        self.speed += min(self.speed + self._cfg.SPEED_STEP, self._cfg.MAX_SPEED)

    def speed_decrement(self) -> None:
        """
        Decrement the value of movement speed by a standard value.
        """
        self.speed = max(self.speed - self._cfg.SPEED_STEP, self._cfg.MIN_SPEED)

    def fire(self, time: float, duration: float) -> None:
        """
        Record a laser fire.
        """
        self.unrecorded_fire = FireInstance(time=time, duration=duration)


@dataclass(kw_only=True, frozen=True)
class FireInstance:
    """
    Data relating to a single fire of the laser.
    """

    time: float
    """
    Time the laser was fired.
    """

    duration: float
    """
    Duration the laser was fired for.
    """
