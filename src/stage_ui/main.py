# module imports
import cv2
import datetime
import os.path
import pandas
import pygame
import pygame_gui
import queue
import serial
import struct
import sys
import time

# these are imports meant to be used as-is
from dataclasses import dataclass
from datetime import datetime as dt
from enum import Enum, IntEnum

# these are imported to be used in type annotations, but when constructing
# objects, fully qualified names are prefered for clarity
from cv2 import VideoCapture
from pandas import DataFrame
from pygame import Clock, Color, Surface, Font
from pygame_gui import UIManager
from pygame_gui.elements import (
    UIButton,
    UIImage,
    UILabel,
    UIPanel,
    UITextBox,
    UITextEntryLine,
)
from queue import Queue, Empty
from serial import Serial

#
# constants
#

# time program started at
PROG_START_TIME: float = time.time()

# margins dictionary to remove all margins
PANEL_NO_MARGINS: dict[str, int] = {
    "top": 0,
    "right": 0,
    "bottom": 0,
    "left": 0,
}

# constants representing directions as passed to arduino
DIRECTION_LEFT: int = 0
DIRECTION_RIGHT: int = 1
DIRECTION_DOWN: int = 2  # away (up)
DIRECTION_UP: int = 3  # towards (down)

# ui theme for pygame_gui
UI_THEME = {"#red_panel": {"colours": {"dark_bg": "#FF0000"}}}

#
# helper data classes & enums
#


class Direction(IntEnum):
    """
    Enum representing possible directions.
    """

    LEFT = DIRECTION_LEFT
    RIGHT = DIRECTION_RIGHT
    DOWN = DIRECTION_DOWN
    UP = DIRECTION_UP

    DEFAULT = LEFT
    """
    A default value for when this enum is needed but its value unused.
    """


class Response(Enum):
    """
    Enum representing all possible worm responses.
    """

    FULL = "F"
    PARTIAL = "P"
    ACKNOWLEDGE = "A"
    NO_RESPONSE = "N"

    def __str__(self) -> str:
        match self:
            case Response.FULL:
                return "F"
            case Response.PARTIAL:
                return "P"
            case Response.ACKNOWLEDGE:
                return "A"
            case Response.NO_RESPONSE:
                return "N"


@dataclass
class Command:
    """
    Data class containing info about a single command to send to the arduino.
    """

    speed: float
    """
    The speed in steps per second of a movement command.
    """

    direction: Direction
    """
    The direction of a movement command.
    """

    move_duration: float
    """
    The duration in milliseconds of a movement command.
    """

    fire_duration: float
    """
    The duration in milliseconds of a fire command.
    """

    def max_duration(self) -> float:
        """
        The theorietical runtime of the command, or the max of the move and fire
        durations.

        :return: The max duration in seconds.
        :rtype: float
        """
        return max(move_duration, fire_duration) / 1000.0

    def packet(self) -> bytes:
        """
        Create a binary packet from this command.

        :return: The binary packet.
        :rtype: bytes
        """

        # # create a packet by manually concating bytes
        # packet = struct.pack("f", -1.0)
        # packet += struct.pack("f", self.speed)
        # packet += struct.pack("f", float(self.direction))
        # packet += struct.pack("f", self.move_duration)
        # packet += struct.pack("f", self.fire_duration)

        # create a packet of 5 float values
        packet: bytes = struct.pack(
            "fffff",
            -1.0,  # header
            self.speed,
            float(self.direction),
            self.move_duration,
            self.fire_duration,
        )

        return packet


#
# config
#

# whether the app should be run in "testing" mode
TESTING: bool = True

# name of the csv datafile to create / write to
DATA_FILE: str = f"data/{dt.now().strftime("%Y-%m-%dT%H%M%S")}-data.csv"

# serial port to connect to arduino on
SERIAL_PORT: str = "COM3"

# baude rate to communicate with arduino at
SERIAL_BAUDRATE: int = 115200

# opencv video capture camera index
CAMERA_INDEX: int = 3 if not TESTING else 0

# max fps to render at
FPS: int = 60

# value to increase speed by
SPEED_STEP: float = 10.0

# min, max, defautlt movement speeds
MIN_SPEED: float = 10.0
MAX_SPEED: float = 1000.0
DEFAULT_SPEED: float = 100.0

# min, max, default laser fire duration (ms)
MIN_FIRE_DURATION: float = 1.0
MAX_FIRE_DURATION: float = 10000.0
DEFAULT_FIRE_DURATION: float = 200.0

# min, max, default size of the square grid
MIN_GRID_SIZE: int = 1
MAX_GRID_SIZE: int = 20
DEFAULT_GRID_SIZE: int = 3

# min, max, default duration for move commands (ms)
MIN_MOVE_DURATION: float = 1.0
MAX_MOVE_DURATION: float = 5000.0
DEFAULT_MOVE_DURATION: float = 100.0

# name of the application
WINDOW_NAME: str = "Stage Controller"

# width of the window
WINDOW_WIDTH: int = 1000

# height of the window
WINDOW_HEIGHT: int = 650

# amount of padding between main panels
WINDOW_SEP: int = 20

# amount of padding between sub-panels
WINDOW_PANEL_SEP: int = 10

# mappings of key constants to directions
DIRECTION_MAP: dict[int, Direction] = {
    pygame.K_h: Direction.LEFT,
    pygame.K_k: Direction.RIGHT,
    pygame.K_u: Direction.UP,
    pygame.K_j: Direction.DOWN,
}

# alternate arrow key contant mappings to directions. should these exist?
DIRECTION_ARROW_MAP: dict[int, Direction] = {
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
}


#
# arduino logic
#


class StageController:
    """
    Class dealing with communication to the arduino.
    """

    def __init__(self) -> None:
        """
        Open a serial connection to the arduino.
        """

        # empty serial connection
        self.ser: Serial | None = None

        # command queue
        self.command_queue: Queue[Command] = queue.Queue()

        # whether blocking (?) commands are executing
        self.is_executing: bool = False

        # start time of executing cmd
        self.current_command_start_time: float | None = None

        # time the executing cmd should take (s)
        self.current_command_duration: float = 0.0

        # try to create serial connection
        try:
            self.ser = serial.Serial(
                port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=0.1
            )
        except Exception as e:
            # print error on connection failure
            print("Serial connection failed:", e)

            # crash program if in prod
            if not TESTING:
                sys.exit(1)

    # send packet via serial connection immediately
    def send_command_immediate(self, command: Command) -> None:
        """
        Send a command to arduino immediately. This is a blocking operation.

        :param command: The command to execute.
        """

        # check for connection
        if not self.ser:
            return

        # write command packet to the serial port
        self.ser.write(command.packet())

        # update internal state to indicate a command is executing
        self.is_executing = True
        self.current_command_start_time = time.time()
        self.current_command_duration = command.max_duration()

    # enqueue a command. is this ever used properly?
    def queue_command(
        self,
        speed: float,
        direction: Direction,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        """Queue a command for non-blocking execution"""

        command: Command = Command(
            speed,
            direction,
            move_duration,
            fire_duration,
        )

        # add to the queue
        self.command_queue.put(command)

    # check and update internal state each frame
    def update(self) -> None:
        """Update command execution state - call this every frame"""

        # if command is executing (with start time present) and command is
        # complete (theoretical execution time has elapsed) set is_executing to
        # False and current_command_start_time to None
        if self.is_executing and self.current_command_start_time:
            if (
                time.time() - self.current_command_start_time
                >= self.current_command_duration
            ):
                self.is_executing = False
                self.current_command_start_time = None

        # if not executing, try to execute a command in queue
        if not self.is_executing:
            try:
                command = self.command_queue.get_nowait()
                self.send_command_immediate(command)
            except Empty:
                pass

    # repeatedly fire laser in a square grid pattern
    def scan_grid(self, n: int, speed: float = 100.0, step_time: float = 10.0) -> None:
        """Queue commands for grid scanning pattern"""

        # loop over number of rows in grid
        for row in range(n):
            # loop over number of columns in grid
            for col in range(n):
                # enqueue move right if not first col in row
                if col > 0:
                    self.queue_command(speed, Direction.RIGHT, step_time, 0)
                # fire laser at current point
                self.queue_command(0, Direction.DEFAULT, 0, 1000)

            # if row is not the last, move left back to first col, then
            # down one to next row
            if row < n - 1:
                # move left until back to col 1
                for _ in range(n - 1):
                    self.queue_command(speed, Direction.LEFT, step_time, 0)
                # move down (?) 1. everything was labeled down but int was 3, so
                # i changed const to indicate up?
                self.queue_command(speed, Direction.UP, step_time, 0)

        # move up to top row. should this also move to left? also this was again
        # 2 but labeled everywhere as up ?
        for _ in range(n - 1):
            self.queue_command(speed, Direction.DOWN, step_time, 0)

    # return if is_executing or if queue is not empty.
    def is_busy(self) -> bool:
        """Check if controller is busy executing commands"""

        return self.is_executing or not self.command_queue.empty()


#
# init
#

# initialize pygame
pygame.init()

# set window title
pygame.display.set_caption(WINDOW_NAME)

# create the display surface
screen: Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# connect to stage controller
stage: StageController = StageController()

# setup ui manager
manager: UIManager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), UI_THEME)

# connect to camera feed
feed: VideoCapture = cv2.VideoCapture(CAMERA_INDEX)
feed_w: int = int(feed.get(cv2.CAP_PROP_FRAME_WIDTH))
feed_h: int = int(feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
feed_a: float = feed_w / feed_h

# default ui font
font: Font = pygame.font.SysFont("Calibri", 20)

#
# state variables
#

# current speed (steps per second)
speed: float = DEFAULT_SPEED

# duration of move commands
move_duration: float = DEFAULT_MOVE_DURATION

# duration of fire commands
fire_duration: float = DEFAULT_FIRE_DURATION

# size of the square grid
grid_size: int = DEFAULT_GRID_SIZE

# if in "marker placement" mode. when True, mouse can be used to place marker on
# camera grid
place_marker: bool = False

# the "normalized coords" of where mouse click placed a marker. should the tuple
# values be floats or ints?
pos_vid: tuple[float, float] | None = None

# time when flash started or None when not flashing
flash_start_time: float | None = None

# time at last laser fire
last_fire_time: float | None = None

# fire duration (radius ?) at last laser fire
last_fire_duration: float | None = None

# room temp in degrees celsius
room_temp: float | None = None

# current strain of worm
worm_strain: str | None = None

# current index / id of worm being recorded
worm_id: str | None = None

# whether data has yet to be recorded since the last laser fire
data_needed: bool = False

# what direction movement is currently happening in
direction: Direction | None = None

# if program is running
running: bool = True

#
# ui components
#

# main panel at top of window with status info
info_panel_w: int = WINDOW_WIDTH - (2 * WINDOW_SEP)
info_panel_h: int = 170
info_panel_x: int = WINDOW_SEP
info_panel_y: int = WINDOW_SEP
info_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(info_panel_x, info_panel_y, info_panel_w, info_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

# panel that flashes while laser is firing
flash_panel_w: int = info_panel_h - (2 * WINDOW_PANEL_SEP)
flash_panel_h: int = info_panel_h - (2 * WINDOW_PANEL_SEP)
flash_panel_x: int = info_panel_w - flash_panel_w - WINDOW_PANEL_SEP
flash_panel_y: int = WINDOW_PANEL_SEP
flash_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        flash_panel_x, flash_panel_y, flash_panel_w, flash_panel_h
    ),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=info_panel,
    object_id=None,
)


def flash_panel_update() -> None:
    global flash_start_time

    if flash_start_time:
        if time.time() - flash_start_time < 0.5:
            flash_panel.change_object_id("#red_panel")
        else:
            flash_panel.change_object_id(None)
            flash_start_time = None


# status text box with current state variables
status_box_w: int = 200
status_box_h: int = info_panel_h - (2 * WINDOW_PANEL_SEP)
status_box_x: int = WINDOW_PANEL_SEP
status_box_y: int = WINDOW_PANEL_SEP
status_box: UITextBox = pygame_gui.elements.UITextBox(
    html_text="",
    relative_rect=pygame.Rect(status_box_x, status_box_y, status_box_w, status_box_h),
    manager=manager,
    container=info_panel,
)


def status_box_update() -> None:
    # name, value pairs
    data: list[tuple[str, str]] = [
        ("Speed", f"{speed:.2f} sps"),
        ("Marker X", f"{pos_vid[0]:.2f}" if pos_vid else "None"),
        ("Marker Y", f"{pos_vid[1]:.2f}" if pos_vid else "None"),
        ("Stage Controller", "Busy" if stage.is_busy() else "Idle"),
    ]

    # constructed html from key-definition pairs
    html: str = "<br>".join([f"<b>{key}:</b> {val}" for key, val in data])

    # update box
    status_box.set_text(html)


# data recording panel
data_panel_w: int = info_panel_w - status_box_w - flash_panel_w - (4 * WINDOW_PANEL_SEP)
data_panel_h: int = info_panel_h - (2 * WINDOW_PANEL_SEP)
data_panel_x: int = status_box_w + (2 * WINDOW_PANEL_SEP)
data_panel_y: int = WINDOW_PANEL_SEP
data_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(data_panel_x, data_panel_y, data_panel_w, data_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=info_panel,
)

data_status_box_w: int = data_panel_w
data_status_box_h: int = data_panel_h
data_status_box_x: int = 0
data_status_box_y: int = 0
data_status_box: UITextBox = pygame_gui.elements.UITextBox(
    html_text="",
    relative_rect=pygame.Rect(
        data_status_box_x, data_status_box_y, data_status_box_w, data_status_box_h
    ),
    manager=manager,
    container=data_panel,
)


def data_status_box_update() -> None:
    # name, value pairs
    data: list[tuple[str, str]] = [
        (
            "Time",
            (
                f"{time.strftime("%Y-%m-%d %H:%M", time.localtime(last_fire_time))}"
                if last_fire_time
                else "None"
            ),
        ),
        ("Temp", f"{room_temp:.1f}" if room_temp is not None else "None"),
        ("Strain", worm_strain if worm_strain else "None"),
        ("ID", worm_id if worm_id else "None"),
        ("Radius", f"{last_fire_duration:.2f} ms" if last_fire_duration else "None"),
    ]

    # constructed html from key-definition pairs
    html: str = "<br>".join([f"<b>{key}:</b> {val}" for key, val in data])

    # update box
    data_status_box.set_text(html)


def create_datafile() -> None:
    df: DataFrame = pandas.DataFrame(
        {
            "fire_time": [],
            "room_temp": [],
            "worm_strain": [],
            "worm_id": [],
            "fire_length": [],
            "response": [],
        }
    )
    df.to_csv(DATA_FILE, index=False)


def data_buttons_handle_press(res: Response) -> None:
    global last_fire_time, data_needed, last_fire_duration

    # create datafile if it doesn't exist
    if not os.path.isfile(DATA_FILE):
        create_datafile()

    # create dataframe from data
    df: DataFrame = pandas.DataFrame(
        {
            "fire_time": [
                datetime.datetime.fromtimestamp(
                    last_fire_time if last_fire_time else 0.0, tz=datetime.timezone.utc
                )
            ],
            "room_temp": [room_temp],
            "worm_strain": [worm_strain],
            "worm_id": [worm_id],
            "fire_length": [fire_duration],
            "response": [str(res)],
        }
    )
    df.to_csv(DATA_FILE, mode="a", index=False, header=False)

    # reset state
    data_needed = False
    last_fire_time = None
    last_fire_duration = None

    # disable buttons
    data_buttons_disable()


# data button constants
DATA_BUTTON_W: int = 75
DATA_BUTTON_H: int = int((data_panel_h - (3 * WINDOW_PANEL_SEP)) / 2)

data_p_button_w: int = DATA_BUTTON_W
data_p_button_h: int = DATA_BUTTON_H
data_p_button_x: int = data_panel_w - DATA_BUTTON_W - WINDOW_PANEL_SEP
data_p_button_y: int = WINDOW_PANEL_SEP
data_p_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        data_p_button_x,
        data_p_button_y,
        data_p_button_w,
        data_p_button_h,
    ),
    text="P",
    manager=manager,
    container=data_panel,
)
data_p_button.bind(
    pygame_gui.UI_BUTTON_PRESSED, lambda: data_buttons_handle_press(Response.PARTIAL)
)

data_n_button_w: int = DATA_BUTTON_W
data_n_button_h: int = DATA_BUTTON_H
data_n_button_x: int = data_panel_w - DATA_BUTTON_W - WINDOW_PANEL_SEP
data_n_button_y: int = DATA_BUTTON_H + (2 * WINDOW_PANEL_SEP)
data_n_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        data_n_button_x,
        data_n_button_y,
        data_n_button_w,
        data_n_button_h,
    ),
    text="N",
    manager=manager,
    container=data_panel,
)
data_n_button.bind(
    pygame_gui.UI_BUTTON_PRESSED,
    lambda: data_buttons_handle_press(Response.NO_RESPONSE),
)

data_f_button_w: int = DATA_BUTTON_W
data_f_button_h: int = DATA_BUTTON_H
data_f_button_x: int = data_panel_w - (2 * DATA_BUTTON_W) - (2 * WINDOW_PANEL_SEP)
data_f_button_y: int = WINDOW_PANEL_SEP
data_f_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        data_f_button_x,
        data_f_button_y,
        data_f_button_w,
        data_f_button_h,
    ),
    text="F",
    manager=manager,
    container=data_panel,
)
data_f_button.bind(
    pygame_gui.UI_BUTTON_PRESSED, lambda: data_buttons_handle_press(Response.FULL)
)

data_a_button_w: int = DATA_BUTTON_W
data_a_button_h: int = DATA_BUTTON_H
data_a_button_x: int = data_panel_w - (2 * DATA_BUTTON_W) - (2 * WINDOW_PANEL_SEP)
data_a_button_y: int = DATA_BUTTON_H + (2 * WINDOW_PANEL_SEP)
data_a_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        data_a_button_x,
        data_a_button_y,
        data_a_button_w,
        data_a_button_h,
    ),
    text="A",
    manager=manager,
    container=data_panel,
)
data_a_button.bind(
    pygame_gui.UI_BUTTON_PRESSED,
    lambda: data_buttons_handle_press(Response.ACKNOWLEDGE),
)


def data_buttons_enable() -> None:
    """
    Enable all the data buttons.
    """

    data_p_button.enable()  # type: ignore[no-untyped-call]
    data_n_button.enable()  # type: ignore[no-untyped-call]
    data_f_button.enable()  # type: ignore[no-untyped-call]
    data_a_button.enable()  # type: ignore[no-untyped-call]


def data_buttons_disable() -> None:
    """
    Disable all the data buttons.
    """

    data_p_button.disable()  # type: ignore[no-untyped-call]
    data_n_button.disable()  # type: ignore[no-untyped-call]
    data_f_button.disable()  # type: ignore[no-untyped-call]
    data_a_button.disable()  # type: ignore[no-untyped-call]


data_buttons_disable()


DATA_INPUT_W: int = 125
DATA_INPUT_H: int = 30
DATA_INPUT_X: int = (
    data_panel_w - (2 * DATA_BUTTON_W) - DATA_INPUT_W - (3 * WINDOW_PANEL_SEP)
)
DATA_LABEL_H: int = 20
DATA_INPUTS_H: int = (2 * DATA_INPUT_H) + (2 * DATA_LABEL_H)
DATA_INPUTS_TOP: int = int((data_panel_h - DATA_INPUTS_H) / 2)

data_id_label_w: int = DATA_INPUT_W
data_id_label_h: int = DATA_LABEL_H
data_id_label_x: int = DATA_INPUT_X
data_id_label_y: int = DATA_INPUTS_TOP
data_id_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        data_id_label_x,
        data_id_label_y,
        data_id_label_w,
        data_id_label_h,
    ),
    text="Worm ID",
    manager=manager,
    container=data_panel,
)

data_id_input_w: int = DATA_INPUT_W
data_id_input_h: int = DATA_INPUT_H
data_id_input_x: int = DATA_INPUT_X
data_id_input_y: int = DATA_INPUTS_TOP + DATA_LABEL_H
data_id_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        data_id_input_x,
        data_id_input_y,
        data_id_input_w,
        data_id_input_h,
    ),
    manager=manager,
    container=data_panel,
    initial_text="",
)


def data_id_input_handle_finish(text: str) -> None:

    # bring state variables into scope to modify
    global worm_id

    # sanitize and update state var
    worm_id = text.strip()


data_strain_label_w: int = DATA_INPUT_W
data_strain_label_h: int = DATA_LABEL_H
data_strain_label_x: int = DATA_INPUT_X
data_strain_label_y: int = DATA_INPUTS_TOP + DATA_LABEL_H + DATA_INPUT_H
data_strain_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        data_strain_label_x,
        data_strain_label_y,
        data_strain_label_w,
        data_strain_label_h,
    ),
    text="Strain",
    manager=manager,
    container=data_panel,
)

data_strain_input_w: int = DATA_INPUT_W
data_strain_input_h: int = DATA_INPUT_H
data_strain_input_x: int = DATA_INPUT_X
data_strain_input_y: int = DATA_INPUTS_TOP + (2 * DATA_LABEL_H) + DATA_INPUT_H
data_strain_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        data_strain_input_x,
        data_strain_input_y,
        data_strain_input_w,
        data_strain_input_h,
    ),
    manager=manager,
    container=data_panel,
    initial_text="",
)


def data_strain_input_handle_finish(text: str) -> None:

    # bring state variables into scope to modify
    global worm_strain

    # update state var
    worm_strain = text.strip()


# main panel at left of window where main ui is held
ui_panel_w: int = 400
ui_panel_h: int = WINDOW_HEIGHT - info_panel_h - (3 * WINDOW_SEP)
ui_panel_x: int = WINDOW_SEP
ui_panel_y: int = info_panel_h + (2 * WINDOW_SEP)
ui_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(ui_panel_x, ui_panel_y, ui_panel_w, ui_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

# sub-panel containing countdown at the bottom of ui_panel
countdown_panel_w: int = ui_panel_w - (2 * WINDOW_PANEL_SEP)
countdown_panel_h: int = 80
countdown_panel_x: int = WINDOW_PANEL_SEP
countdown_panel_y: int = ui_panel_h - countdown_panel_h - WINDOW_PANEL_SEP
countdown_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        countdown_panel_x, countdown_panel_y, countdown_panel_w, countdown_panel_h
    ),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=ui_panel,
)

# label displaying timer inside countdown_panel
countdown_label_w: int = countdown_panel_w
countdown_label_h: int = countdown_panel_h
countdown_label_x: int = 0
countdown_label_y: int = 0
countdown_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        countdown_label_x, countdown_label_y, countdown_label_w, countdown_label_h
    ),
    text="Countdown: 00s",
    manager=manager,
    container=countdown_panel,
)


def countdown_label_update() -> None:
    """
    Update the countdown_label to reflect the time remaining. Should be called
    once per frame.
    """

    # calculate the remaining time of the 15 second countdown label
    remaining_time: int = 15 - (int(time.time() - PROG_START_TIME) % 16)

    # update the countdown label's text
    countdown_label.set_text(f"Countdown: {remaining_time}s")


# button for activating "place marker" mode above the countdown in ui_panel
marker_button_w: int = ui_panel_w - (2 * WINDOW_PANEL_SEP)
marker_button_h: int = 120
marker_button_x: int = WINDOW_PANEL_SEP
marker_button_y: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (2 * WINDOW_PANEL_SEP)
)
marker_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        marker_button_x, marker_button_y, marker_button_w, marker_button_h
    ),
    text="Place Laser Marker",
    manager=manager,
    container=ui_panel,
)


def marker_button_handle_press() -> None:
    """
    When marker_button is pressed, put the application into "place marker" mode
    and disable the button.
    """

    # bring state variables into scope to modify. i don't love this strategy,
    # but for now it works
    global place_marker

    # update state
    place_marker = True
    marker_button.disable()  # type: ignore[no-untyped-call]


marker_button.bind(pygame_gui.UI_BUTTON_PRESSED, marker_button_handle_press)


# ui panel containing numeric inputs on top left of ui_panel
numeric_inputs_panel_w: int = 150
numeric_inputs_panel_h: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (4 * WINDOW_PANEL_SEP)
)
numeric_inputs_panel_x: int = WINDOW_PANEL_SEP
numeric_inputs_panel_y: int = WINDOW_PANEL_SEP
numeric_inputs_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        numeric_inputs_panel_x,
        numeric_inputs_panel_y,
        numeric_inputs_panel_w,
        numeric_inputs_panel_h,
    ),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=ui_panel,
)

# label for fire duration inside numeric_inputs_panel
fire_duration_label_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
fire_duration_label_h: int = 30
fire_duration_label_x: int = WINDOW_PANEL_SEP
fire_duration_label_y: int = WINDOW_PANEL_SEP
fire_duration_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        fire_duration_label_x,
        fire_duration_label_y,
        fire_duration_label_w,
        fire_duration_label_h,
    ),
    text="FireLength(ms)",
    manager=manager,
    container=numeric_inputs_panel,
)

# input for fire duration inside numeric_inputs_panel
fire_duration_input_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
fire_duration_input_h: int = 30
fire_duration_input_x: int = WINDOW_PANEL_SEP
fire_duration_input_y: int = WINDOW_PANEL_SEP + 25
fire_duration_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        fire_duration_input_x,
        fire_duration_input_y,
        fire_duration_input_w,
        fire_duration_input_h,
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(int(DEFAULT_FIRE_DURATION)),
)


def fire_duration_input_handle_finish(text: str) -> None:
    """
    When fire_duration_input is complete, update the fire_duration state
    variable.

    :param text: The user entered text.
    """

    # bring state variables into scope to modify. i don't love this strategy,
    # but for now it works
    global fire_duration

    # parse and update state var
    try:
        val = float(text)
        fire_duration = (
            val if MIN_FIRE_DURATION <= val <= MAX_FIRE_DURATION else fire_duration
        )
    except:
        ...

    # update text input
    fire_duration_input.set_text(str(int(fire_duration)))


# label for grid size inside numeric_inputs_panel
grid_size_label_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
grid_size_label_h: int = 30
grid_size_label_x: int = WINDOW_PANEL_SEP
grid_size_label_y: int = WINDOW_PANEL_SEP + 50
grid_size_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        grid_size_label_x, grid_size_label_y, grid_size_label_w, grid_size_label_h
    ),
    text="GridSize(NxN)",
    manager=manager,
    container=numeric_inputs_panel,
)

# input for grid size inside numeric_inputs_panel
grid_size_input_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
grid_size_input_h: int = 30
grid_size_input_x: int = WINDOW_PANEL_SEP
grid_size_input_y: int = WINDOW_PANEL_SEP + 75
grid_size_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        grid_size_input_x, grid_size_input_y, grid_size_input_w, grid_size_input_h
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(DEFAULT_GRID_SIZE),
)


def grid_size_input_handle_finish(text: str) -> None:
    """
    When grid_size_input is complete, update the grid_size state variable.

    :param text: The user entered text.
    """

    # bring state variables into scope to modify. i don't love this strategy,
    # but for now it works
    global grid_size

    # parse and update state var
    try:
        val = int(text)
        grid_size = val if MIN_GRID_SIZE <= val <= MAX_GRID_SIZE else grid_size
    except:
        ...

    # update text input
    grid_size_input.set_text(str(grid_size))


# label for move duration inside numeric_inputs_panel
move_duration_label_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
move_duration_label_h: int = 30
move_duration_label_x: int = WINDOW_PANEL_SEP
move_duration_label_y: int = WINDOW_PANEL_SEP + 100
move_duration_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        move_duration_label_x,
        move_duration_label_y,
        move_duration_label_w,
        move_duration_label_h,
    ),
    text="MoveDuration(ms)",
    manager=manager,
    container=numeric_inputs_panel,
)

# input for move duration inside numeric_inputs_panel
move_duration_input_w: int = numeric_inputs_panel_w - (2 * WINDOW_PANEL_SEP)
move_duration_input_h: int = 30
move_duration_input_x: int = WINDOW_PANEL_SEP
move_duration_input_y: int = WINDOW_PANEL_SEP + 125
move_duration_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        move_duration_input_x,
        move_duration_input_y,
        move_duration_input_w,
        move_duration_input_h,
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(int(DEFAULT_MOVE_DURATION)),
)


def move_duration_input_handle_finish(text: str) -> None:

    # bring state variables into scope to modify. i don't love this strategy,
    # but for now it works
    global move_duration

    # parse and update state var
    try:
        val = float(text)
        move_duration = (
            val if MIN_MOVE_DURATION <= val <= MAX_MOVE_DURATION else move_duration
        )
    except:
        ...

    # update text input
    move_duration_input.set_text(str(int(move_duration)))


# ui panel containing help info on top right of ui_panel
help_panel_w: int = ui_panel_w - numeric_inputs_panel_w - (3 * WINDOW_PANEL_SEP)
help_panel_h: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (4 * WINDOW_PANEL_SEP)
)
help_panel_x: int = numeric_inputs_panel_w + (2 * WINDOW_PANEL_SEP)
help_panel_y: int = WINDOW_PANEL_SEP
help_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(help_panel_x, help_panel_y, help_panel_w, help_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=ui_panel,
)

# key-definition pairs for help menu
key_labels_data: list[tuple[str, str]] = [
    ("h", "Move Left"),
    ("j", "Move Down"),
    ("k", "Move Right"),
    ("u", "Move Up"),
    ("f", "Fire Laser"),
    ("m", "Shoot and Step Grid"),
    ("w", "Speed Increase"),
    ("s", "Speed Decrease"),
    ("p", "Skip Data"),
    ("Enter", "Sets Inputs"),
    ("Esc", "Shut Down"),
]

# constructed html from key-definition pairs
key_labels_html: str = "<br>".join(
    [f"<b>{key}:</b> {desc}" for key, desc in key_labels_data]
)

# text box containing key-definition pairs
key_labels_box_w: int = help_panel_w - (2 * WINDOW_PANEL_SEP)
key_labels_box_h: int = help_panel_h - (2 * WINDOW_PANEL_SEP)
key_labels_box_x: int = WINDOW_PANEL_SEP
key_labels_box_y: int = WINDOW_PANEL_SEP
key_labels_box: UITextBox = pygame_gui.elements.UITextBox(
    html_text=key_labels_html,
    relative_rect=pygame.Rect(
        key_labels_box_x, key_labels_box_y, key_labels_box_w, key_labels_box_h
    ),
    manager=manager,
    container=help_panel,
)

# panel containing the video feed
video_panel_w: int = WINDOW_WIDTH - ui_panel_w - (3 * WINDOW_SEP)
video_panel_h: int = WINDOW_HEIGHT - info_panel_h - (3 * WINDOW_SEP)
video_panel_x: int = ui_panel_w + (2 * WINDOW_SEP)
video_panel_y: int = info_panel_h + (2 * WINDOW_SEP)
video_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        video_panel_x, video_panel_y, video_panel_w, video_panel_h
    ),
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

# container for the current frame from the camera
video_frame_p: float = (
    0.95  # padding factor (fraction of video_panel to use as padding)
)
video_frame_s: float = (
    video_frame_p * (video_panel_w / feed_w)
    if video_panel_w / video_panel_h <= feed_a
    else video_frame_p * (video_panel_h / feed_w)
)  # scaling factor (amount to scale the width and height by)
video_frame_w: int = int(video_frame_s * feed_w)
video_frame_h: int = int(video_frame_s * feed_h)
video_frame_x: int = int((video_panel_w / 2) - ((video_frame_s * feed_w) / 2))
video_frame_y: int = int((video_panel_h / 2) - ((video_frame_s * feed_h) / 2))
video_frame: UIImage = pygame_gui.elements.UIImage(
    relative_rect=pygame.Rect(
        video_frame_x, video_frame_y, video_frame_w, video_frame_h
    ),
    image_surface=pygame.Surface((video_frame_w, video_frame_h)),
    manager=manager,
    container=video_panel,
)


def video_frame_collidepoint(x: int, y: int) -> bool:
    return (0 < (x - video_panel_x - video_frame_x) < (video_frame_s * feed_w)) and (
        0 < (y - video_panel_y - video_frame_y) < (video_frame_s * feed_h)
    )


def video_frame_place_marker(x: int, y: int) -> None:
    # bring state variables into scope to modify. i don't love this strategy,
    # but for now it works
    global pos_vid, place_marker

    # convert absolute x and y values to "normalized coords". should these be
    # converted to ints?
    relative_x: float = (
        (x - video_panel_x - video_frame_x) / (video_frame_s * feed_w)
    ) * 500
    relative_y: float = (
        (y - video_panel_y - video_frame_y) / (video_frame_s * feed_h)
    ) * 500

    # update state
    pos_vid = (relative_x, relative_y)
    marker_button.enable()  # type: ignore[no-untyped-call]
    place_marker = False


def video_frame_update() -> None:
    # get frame from feed. this is blocking and might be bad to be in our UI
    # thread? that seems like an issue that can be addressed later
    read_success, feed_frame = feed.read()

    # break early on no frame
    if not read_success:
        return

    # rotate frame to correct orientation and convert from bgr to rgb due to
    # differences between cv2 format and pygame format
    feed_frame = cv2.rotate(feed_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    feed_frame = cv2.cvtColor(feed_frame, cv2.COLOR_BGR2RGB)

    # create surface from frame and scale to 500 by 500
    frame_surface: Surface = pygame.surfarray.make_surface(feed_frame)
    frame_surface = pygame.transform.scale(frame_surface, (500, 500))

    # font
    label_font: Font = pygame.font.SysFont("Arial", 14)

    # config
    GRID_SPACING: int = 40
    GRID_COLOR: Color = pygame.Color(183, 53, 219)
    GRID_LINE_WDITH: int = 1
    GRID_LABEL_COLOR: Color = pygame.Color(245, 235, 44)

    # width and height of frame surface (isn't this just 500 and 500)
    frame_surface_w, frame_surface_h = frame_surface.get_size()

    # draw vertical lines with labels
    for x in range(0, frame_surface_w, GRID_SPACING):
        pygame.draw.line(
            frame_surface, GRID_COLOR, (x, 0), (x, frame_surface_h), GRID_LINE_WDITH
        )
        label = label_font.render(f"{x}", True, GRID_LABEL_COLOR)
        frame_surface.blit(label, (x + 2, 2))

    # draw horizontal lines
    for y in range(0, frame_surface_h, GRID_SPACING):
        pygame.draw.line(
            frame_surface, GRID_COLOR, (0, y), (frame_surface_w, y), GRID_LINE_WDITH
        )
        label = label_font.render(f"{y}", True, GRID_LABEL_COLOR)
        frame_surface.blit(label, (2, y + 2))

    # label for something? i have no idea what this means
    pixel_size = 10
    pixel_label = label_font.render(
        f"{GRID_SPACING * pixel_size}", True, GRID_LABEL_COLOR
    )
    frame_surface.blit(pixel_label, (frame_surface_w - 80, frame_surface_h - 20))

    # draw marker
    if pos_vid:
        # red circle with radius 5
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(255, 0, 0),
            center=pos_vid,
            radius=5,
            width=2,
        )
        # green circle with radius 25
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(0, 255, 0),
            center=pos_vid,
            radius=25,
            width=1,
        )
        # blue circle with radius 45
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(0, 0, 255),
            center=pos_vid,
            radius=45,
            width=1,
        )
        # yellow circle with radius 65
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(255, 255, 0),
            center=pos_vid,
            radius=65,
            width=1,
        )

    # set image
    video_frame.set_image(frame_surface)


temp_window_w: int = 300
temp_window_h: int = 150
temp_window_x: int = int(WINDOW_WIDTH / 2) - int(temp_window_w / 2)
temp_window_y: int = int(WINDOW_HEIGHT / 2) - int(temp_window_h / 2)
temp_window: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        temp_window_x, temp_window_y, temp_window_w, temp_window_h
    ),
    starting_height=10,
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

temp_window_label_w: int = temp_window_w
temp_window_label_h: int = 20
temp_window_label_x: int = 0
temp_window_label_y: int = int(temp_window_h / 2) - 30
temp_window_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        temp_window_label_x,
        temp_window_label_y,
        temp_window_label_w,
        temp_window_label_h,
    ),
    text="Please set the room temp (\u2103).",
    manager=manager,
    container=temp_window,
)

temp_window_input_w: int = 125
temp_window_input_h: int = 30
temp_window_input_x: int = int(temp_window_w / 2) - int(temp_window_input_w / 2)
temp_window_input_y: int = temp_window_label_y + 30
temp_window_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        temp_window_input_x,
        temp_window_input_y,
        temp_window_input_w,
        temp_window_input_h,
    ),
    manager=manager,
    container=temp_window,
    initial_text="",
)


def temp_window_input_handle_finish(text: str) -> None:

    # bring state variables into scope to modify
    global room_temp

    # parse and update state var
    try:
        val = float(text)
        if val == 0:
            raise Exception()
        room_temp = val
    except:
        room_temp = None
        return

    # diable and hide temp window
    temp_window.disable()  # type: ignore[no-untyped-call]
    temp_window.hide()


#
# main loop
#


# clock
clock: Clock = pygame.Clock()

while running:

    #
    # temporal values
    #

    # time in seconds since last frame
    time_delta: float = clock.tick(FPS) / 1000.0

    #
    # event-based updates
    #

    for event in pygame.event.get():
        # handle events manually
        match event.type:

            # quit app
            case pygame.QUIT:
                running = False

            # keypress
            case pygame.KEYDOWN:
                keydown_key: int = event.key
                match keydown_key:
                    # quit
                    case pygame.K_ESCAPE:
                        running = False
                    # increase speed
                    case pygame.K_w:
                        speed = min(speed + SPEED_STEP, MAX_SPEED)
                    # decrease speed
                    case pygame.K_s:
                        speed = max(speed - SPEED_STEP, MIN_SPEED)
                    # fire
                    case pygame.K_f if not data_needed:
                        stage.send_command_immediate(
                            Command(0.0, Direction.DEFAULT, 0.0, fire_duration)
                        )
                        now = time.time()

                        # update state
                        data_needed = True
                        flash_start_time = now
                        last_fire_time = now
                        last_fire_duration = fire_duration

                        # enable buttons
                        data_buttons_enable()

                    # scan grid
                    case pygame.K_m if not stage.is_busy():
                        stage.scan_grid(grid_size, speed=speed, step_time=move_duration)
                        flash_start_time = time.time()

                    # skip data
                    case pygame.K_p:
                        data_needed = False
                        last_fire_time = None
                        last_fire_duration = None

                        # disable buttons
                        data_buttons_disable()

                    # move
                    case key if key in DIRECTION_MAP:
                        direction = DIRECTION_MAP[key]
                    # move with arrows, should this be removed?
                    case key if key in DIRECTION_ARROW_MAP:
                        direction = DIRECTION_ARROW_MAP[key]

            # key un-press
            case pygame.KEYUP:
                keyup_key: int = event.key
                if (
                    keyup_key in DIRECTION_MAP and direction is DIRECTION_MAP[keyup_key]
                ) or (
                    keyup_key in DIRECTION_ARROW_MAP
                    and direction is DIRECTION_ARROW_MAP[keyup_key]
                ):
                    direction = None

            # mouse click
            case pygame.MOUSEBUTTONDOWN:
                event_pos: tuple[int, int] = event.pos
                event_button: int = event.button
                over_video_frame = video_frame_collidepoint(event_pos[0], event_pos[1])
                match event_button:
                    # left mouse button, in place_marker mode, and over video
                    case 1 if place_marker and over_video_frame:
                        video_frame_place_marker(event_pos[0], event_pos[1])

            # text entry complete (enter is pressed when selected)
            case pygame_gui.UI_TEXT_ENTRY_FINISHED:
                event_ui_element: UITextEntryLine = event.ui_element
                event_text: str = event.text
                match event_ui_element:
                    case e if e is data_id_input:
                        data_id_input_handle_finish(event_text)
                    case e if e is data_strain_input:
                        data_strain_input_handle_finish(event_text)
                    case e if e is fire_duration_input:
                        fire_duration_input_handle_finish(event_text)
                    case e if e is grid_size_input:
                        grid_size_input_handle_finish(event_text)
                    case e if e is move_duration_input:
                        move_duration_input_handle_finish(event_text)
                    case e if e is temp_window_input:
                        temp_window_input_handle_finish(event_text)

        # let manager process event
        manager.process_events(event)

    #
    # update logic: updates independent of events, once every frame or dependent
    #               on time_delta
    #

    # process queued commands
    stage.update()

    # update the countdown to reflect time remaining
    countdown_label_update()

    # update video frame
    video_frame_update()

    # update status box text
    status_box_update()

    # update data recording status box text
    data_status_box_update()

    # update flash box
    flash_panel_update()

    # do movement
    if direction is not None:
        stage.send_command_immediate(Command(speed, direction, move_duration, 0.0))
        print(f"moving {direction}")

        # this is bad
        time.sleep(0.1)

    # have manager update elements
    manager.update(time_delta)

    #
    # draw ui
    #

    # fill window surface with grey color
    screen.fill(pygame.Color(120, 120, 120))

    # let pygame_gui render ui to screen
    manager.draw_ui(screen)

    #
    # update screen
    #

    # update display
    pygame.display.flip()

# exit ui
pygame.quit()
