# module imports
import cv2
import datetime
import pygame
import pygame_gui
import time

# item imports
from cv2 import VideoCapture
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

# local module imports
import constants

# local item imports
from data import DataHandler, Response
from errors import InvalidStateError
from serial_bridge import SerialBridge
from state import State


#
# constants
#

# margins dictionary to remove all margins
PANEL_NO_MARGINS: dict[str, int] = {
    "top": 0,
    "right": 0,
    "bottom": 0,
    "left": 0,
}

# ui theme for pygame_gui
UI_THEME = {"#red_panel": {"colours": {"dark_bg": "#FF0000"}}}


#
# init
#

# initialize pygame
pygame.init()

# set window title
pygame.display.set_caption(constants.WINDOW_NAME)

# create the display surface
screen: Surface = pygame.display.set_mode(
    (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
)

# connect to stage controller
stage: SerialBridge = SerialBridge()

# create data handler
data: DataHandler = DataHandler(constants.DATA_FILE)

# setup ui manager
manager: UIManager = pygame_gui.UIManager(
    (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT), UI_THEME
)

# connect to camera feed
feed: VideoCapture = cv2.VideoCapture(constants.CAMERA_INDEX)
feed_w: int = int(feed.get(cv2.CAP_PROP_FRAME_WIDTH))
feed_h: int = int(feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
feed_a: float = feed_w / feed_h

# default ui font
font: Font = pygame.font.SysFont("Calibri", 20)

# current state
state: State = State()

#
# ui components
#

# main panel at top of window with status info
info_panel_w: int = constants.WINDOW_WIDTH - (2 * constants.WINDOW_SEP)
info_panel_h: int = 170
info_panel_x: int = constants.WINDOW_SEP
info_panel_y: int = constants.WINDOW_SEP
info_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(info_panel_x, info_panel_y, info_panel_w, info_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

# panel that flashes while laser is firing
flash_panel_w: int = info_panel_h - (2 * constants.WINDOW_PANEL_SEP)
flash_panel_h: int = info_panel_h - (2 * constants.WINDOW_PANEL_SEP)
flash_panel_x: int = info_panel_w - flash_panel_w - constants.WINDOW_PANEL_SEP
flash_panel_y: int = constants.WINDOW_PANEL_SEP
flash_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(
        flash_panel_x, flash_panel_y, flash_panel_w, flash_panel_h
    ),
    manager=manager,
    margins=PANEL_NO_MARGINS,
    container=info_panel,
    object_id=None,
)


def flash_panel_update(state: State) -> None:
    if state.flash_start_time:
        if time.time() - state.flash_start_time < 0.5:
            flash_panel.change_object_id("#red_panel")
        else:
            flash_panel.change_object_id(None)
            state.flash_start_time = None


# status text box with current state variables
status_box_w: int = 200
status_box_h: int = info_panel_h - (2 * constants.WINDOW_PANEL_SEP)
status_box_x: int = constants.WINDOW_PANEL_SEP
status_box_y: int = constants.WINDOW_PANEL_SEP
status_box: UITextBox = pygame_gui.elements.UITextBox(
    html_text="",
    relative_rect=pygame.Rect(status_box_x, status_box_y, status_box_w, status_box_h),
    manager=manager,
    container=info_panel,
)


def status_box_update(state: State) -> None:
    # name, value pairs
    data: list[tuple[str, str]] = [
        ("Speed", f"{state.speed:.2f} sps"),
        ("Marker X", f"{state.pos_vid[0]:.2f}" if state.pos_vid else "None"),
        ("Marker Y", f"{state.pos_vid[1]:.2f}" if state.pos_vid else "None"),
        ("Stage Controller", "Busy" if stage.is_busy() else "Idle"),
    ]

    # constructed html from key-definition pairs
    html: str = "<br>".join([f"<b>{key}:</b> {val}" for key, val in data])

    # update box
    status_box.set_text(html)


# data recording panel
data_panel_w: int = (
    info_panel_w - status_box_w - flash_panel_w - (4 * constants.WINDOW_PANEL_SEP)
)
data_panel_h: int = info_panel_h - (2 * constants.WINDOW_PANEL_SEP)
data_panel_x: int = status_box_w + (2 * constants.WINDOW_PANEL_SEP)
data_panel_y: int = constants.WINDOW_PANEL_SEP
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


def data_status_box_update(state: State) -> None:
    # name, value pairs
    data: list[tuple[str, str]] = [
        (
            "Time",
            (
                f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(state.last_fire_time))}"
                if state.last_fire_time
                else "None"
            ),
        ),
        ("Temp", f"{state.room_temp:.1f}" if state.room_temp is not None else "None"),
        ("Strain", state.worm_strain if state.worm_strain else "None"),
        ("ID", state.worm_id if state.worm_id else "None"),
        (
            "Radius",
            (
                f"{state.last_fire_duration:.2f} ms"
                if state.last_fire_duration
                else "None"
            ),
        ),
    ]

    # constructed html from key-definition pairs
    html: str = "<br>".join([f"<b>{key}:</b> {val}" for key, val in data])

    # update box
    data_status_box.set_text(html)


def data_buttons_handle_press(state: State, res: Response) -> None:
    # check for invariants
    if (
        state.last_fire_time is None
        or state.last_fire_duration is None
        or state.worm_strain is None
        or state.worm_id is None
        or state.room_temp is None
    ):
        raise InvalidStateError("Impossible State")

    # add data entry
    data.add_entry(
        datetime.datetime.fromtimestamp(state.last_fire_time),
        state.last_fire_duration,
        state.worm_strain,
        state.worm_id,
        res,
        state.room_temp,
    )

    # reset state
    state.data_needed = False
    state.last_fire_time = None
    state.last_fire_duration = None

    # disable buttons
    data_buttons_disable()


# data button constants
DATA_BUTTON_W: int = 75
DATA_BUTTON_H: int = int((data_panel_h - (3 * constants.WINDOW_PANEL_SEP)) / 2)

data_p_button_w: int = DATA_BUTTON_W
data_p_button_h: int = DATA_BUTTON_H
data_p_button_x: int = data_panel_w - DATA_BUTTON_W - constants.WINDOW_PANEL_SEP
data_p_button_y: int = constants.WINDOW_PANEL_SEP
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
    pygame_gui.UI_BUTTON_PRESSED,
    lambda: data_buttons_handle_press(state, Response.PARTIAL),
)

data_n_button_w: int = DATA_BUTTON_W
data_n_button_h: int = DATA_BUTTON_H
data_n_button_x: int = data_panel_w - DATA_BUTTON_W - constants.WINDOW_PANEL_SEP
data_n_button_y: int = DATA_BUTTON_H + (2 * constants.WINDOW_PANEL_SEP)
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
    lambda: data_buttons_handle_press(state, Response.NO_RESPONSE),
)

data_f_button_w: int = DATA_BUTTON_W
data_f_button_h: int = DATA_BUTTON_H
data_f_button_x: int = (
    data_panel_w - (2 * DATA_BUTTON_W) - (2 * constants.WINDOW_PANEL_SEP)
)
data_f_button_y: int = constants.WINDOW_PANEL_SEP
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
    pygame_gui.UI_BUTTON_PRESSED,
    lambda: data_buttons_handle_press(state, Response.FULL),
)

data_a_button_w: int = DATA_BUTTON_W
data_a_button_h: int = DATA_BUTTON_H
data_a_button_x: int = (
    data_panel_w - (2 * DATA_BUTTON_W) - (2 * constants.WINDOW_PANEL_SEP)
)
data_a_button_y: int = DATA_BUTTON_H + (2 * constants.WINDOW_PANEL_SEP)
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
    lambda: data_buttons_handle_press(state, Response.ACKNOWLEDGE),
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
    data_panel_w - (2 * DATA_BUTTON_W) - DATA_INPUT_W - (3 * constants.WINDOW_PANEL_SEP)
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


def data_id_input_handle_finish(state: State, text: str) -> None:
    # sanitize and update state var
    state.worm_id = text.strip()


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


def data_strain_input_handle_finish(state: State, text: str) -> None:
    # update state var
    state.worm_strain = text.strip()


# main panel at left of window where main ui is held
ui_panel_w: int = 400
ui_panel_h: int = constants.WINDOW_HEIGHT - info_panel_h - (3 * constants.WINDOW_SEP)
ui_panel_x: int = constants.WINDOW_SEP
ui_panel_y: int = info_panel_h + (2 * constants.WINDOW_SEP)
ui_panel: UIPanel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(ui_panel_x, ui_panel_y, ui_panel_w, ui_panel_h),
    manager=manager,
    margins=PANEL_NO_MARGINS,
)

# sub-panel containing countdown at the bottom of ui_panel
countdown_panel_w: int = ui_panel_w - (2 * constants.WINDOW_PANEL_SEP)
countdown_panel_h: int = 80
countdown_panel_x: int = constants.WINDOW_PANEL_SEP
countdown_panel_y: int = ui_panel_h - countdown_panel_h - constants.WINDOW_PANEL_SEP
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
    remaining_time: int = 15 - (int(time.time() - constants.PROG_START_TIME) % 16)

    # update the countdown label's text
    countdown_label.set_text(f"Countdown: {remaining_time}s")


# button for activating "place marker" mode above the countdown in ui_panel
marker_button_w: int = ui_panel_w - (2 * constants.WINDOW_PANEL_SEP)
marker_button_h: int = 120
marker_button_x: int = constants.WINDOW_PANEL_SEP
marker_button_y: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (2 * constants.WINDOW_PANEL_SEP)
)
marker_button: UIButton = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        marker_button_x, marker_button_y, marker_button_w, marker_button_h
    ),
    text="Place Laser Marker",
    manager=manager,
    container=ui_panel,
)


def marker_button_handle_press(state: State) -> None:
    """
    When marker_button is pressed, put the application into "place marker" mode
    and disable the button.
    """

    # update state
    state.place_marker = True
    marker_button.disable()  # type: ignore[no-untyped-call]


marker_button.bind(pygame_gui.UI_BUTTON_PRESSED, marker_button_handle_press)


# ui panel containing numeric inputs on top left of ui_panel
numeric_inputs_panel_w: int = 150
numeric_inputs_panel_h: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (4 * constants.WINDOW_PANEL_SEP)
)
numeric_inputs_panel_x: int = constants.WINDOW_PANEL_SEP
numeric_inputs_panel_y: int = constants.WINDOW_PANEL_SEP
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
fire_duration_label_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
fire_duration_label_h: int = 30
fire_duration_label_x: int = constants.WINDOW_PANEL_SEP
fire_duration_label_y: int = constants.WINDOW_PANEL_SEP
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
fire_duration_input_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
fire_duration_input_h: int = 30
fire_duration_input_x: int = constants.WINDOW_PANEL_SEP
fire_duration_input_y: int = constants.WINDOW_PANEL_SEP + 25
fire_duration_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        fire_duration_input_x,
        fire_duration_input_y,
        fire_duration_input_w,
        fire_duration_input_h,
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(int(constants.DEFAULT_FIRE_DURATION)),
)


def fire_duration_input_handle_finish(state: State, text: str) -> None:
    """
    When fire_duration_input is complete, update the fire_duration state
    variable.

    :param text: The user entered text.
    """

    # parse and update state var
    try:
        val = float(text)
        state.fire_duration = (
            val
            if constants.MIN_FIRE_DURATION <= val <= constants.MAX_FIRE_DURATION
            else state.fire_duration
        )
    except Exception:
        ...

    # update text input
    fire_duration_input.set_text(str(int(state.fire_duration)))


# label for grid size inside numeric_inputs_panel
grid_size_label_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
grid_size_label_h: int = 30
grid_size_label_x: int = constants.WINDOW_PANEL_SEP
grid_size_label_y: int = constants.WINDOW_PANEL_SEP + 50
grid_size_label: UILabel = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        grid_size_label_x, grid_size_label_y, grid_size_label_w, grid_size_label_h
    ),
    text="GridSize(NxN)",
    manager=manager,
    container=numeric_inputs_panel,
)

# input for grid size inside numeric_inputs_panel
grid_size_input_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
grid_size_input_h: int = 30
grid_size_input_x: int = constants.WINDOW_PANEL_SEP
grid_size_input_y: int = constants.WINDOW_PANEL_SEP + 75
grid_size_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        grid_size_input_x, grid_size_input_y, grid_size_input_w, grid_size_input_h
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(constants.DEFAULT_GRID_SIZE),
)


def grid_size_input_handle_finish(state: State, text: str) -> None:
    """
    When grid_size_input is complete, update the grid_size state variable.

    :param text: The user entered text.
    """

    # parse and update state var
    try:
        val = int(text)
        state.grid_size = (
            val
            if constants.MIN_GRID_SIZE <= val <= constants.MAX_GRID_SIZE
            else state.grid_size
        )
    except Exception:
        ...

    # update text input
    grid_size_input.set_text(str(state.grid_size))


# label for move duration inside numeric_inputs_panel
move_duration_label_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
move_duration_label_h: int = 30
move_duration_label_x: int = constants.WINDOW_PANEL_SEP
move_duration_label_y: int = constants.WINDOW_PANEL_SEP + 100
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
move_duration_input_w: int = numeric_inputs_panel_w - (2 * constants.WINDOW_PANEL_SEP)
move_duration_input_h: int = 30
move_duration_input_x: int = constants.WINDOW_PANEL_SEP
move_duration_input_y: int = constants.WINDOW_PANEL_SEP + 125
move_duration_input: UITextEntryLine = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        move_duration_input_x,
        move_duration_input_y,
        move_duration_input_w,
        move_duration_input_h,
    ),
    manager=manager,
    container=numeric_inputs_panel,
    initial_text=str(int(constants.DEFAULT_MOVE_DURATION)),
)


def move_duration_input_handle_finish(state: State, text: str) -> None:
    # parse and update state var
    try:
        val = float(text)
        state.move_duration = (
            val
            if constants.MIN_MOVE_DURATION <= val <= constants.MAX_MOVE_DURATION
            else state.move_duration
        )
    except Exception:
        ...

    # update text input
    move_duration_input.set_text(str(int(state.move_duration)))


# ui panel containing help info on top right of ui_panel
help_panel_w: int = (
    ui_panel_w - numeric_inputs_panel_w - (3 * constants.WINDOW_PANEL_SEP)
)
help_panel_h: int = (
    ui_panel_h - countdown_panel_h - marker_button_h - (4 * constants.WINDOW_PANEL_SEP)
)
help_panel_x: int = numeric_inputs_panel_w + (2 * constants.WINDOW_PANEL_SEP)
help_panel_y: int = constants.WINDOW_PANEL_SEP
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
key_labels_box_w: int = help_panel_w - (2 * constants.WINDOW_PANEL_SEP)
key_labels_box_h: int = help_panel_h - (2 * constants.WINDOW_PANEL_SEP)
key_labels_box_x: int = constants.WINDOW_PANEL_SEP
key_labels_box_y: int = constants.WINDOW_PANEL_SEP
key_labels_box: UITextBox = pygame_gui.elements.UITextBox(
    html_text=key_labels_html,
    relative_rect=pygame.Rect(
        key_labels_box_x, key_labels_box_y, key_labels_box_w, key_labels_box_h
    ),
    manager=manager,
    container=help_panel,
)

# panel containing the video feed
video_panel_w: int = constants.WINDOW_WIDTH - ui_panel_w - (3 * constants.WINDOW_SEP)
video_panel_h: int = constants.WINDOW_HEIGHT - info_panel_h - (3 * constants.WINDOW_SEP)
video_panel_x: int = ui_panel_w + (2 * constants.WINDOW_SEP)
video_panel_y: int = info_panel_h + (2 * constants.WINDOW_SEP)
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


def video_frame_place_marker(state: State, x: int, y: int) -> None:
    # convert absolute x and y values to "normalized coords". should these be
    # converted to ints?
    relative_x: float = (
        (x - video_panel_x - video_frame_x) / (video_frame_s * feed_w)
    ) * 500
    relative_y: float = (
        (y - video_panel_y - video_frame_y) / (video_frame_s * feed_h)
    ) * 500

    # update state
    state.pos_vid = (relative_x, relative_y)
    marker_button.enable()  # type: ignore[no-untyped-call]
    state.place_marker = False


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
    if state.pos_vid:
        # red circle with radius 5
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(255, 0, 0),
            center=state.pos_vid,
            radius=5,
            width=2,
        )
        # green circle with radius 25
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(0, 255, 0),
            center=state.pos_vid,
            radius=25,
            width=1,
        )
        # blue circle with radius 45
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(0, 0, 255),
            center=state.pos_vid,
            radius=45,
            width=1,
        )
        # yellow circle with radius 65
        pygame.draw.circle(
            surface=frame_surface,
            color=pygame.Color(255, 255, 0),
            center=state.pos_vid,
            radius=65,
            width=1,
        )

    # set image
    video_frame.set_image(frame_surface)


temp_window_w: int = 300
temp_window_h: int = 150
temp_window_x: int = int(constants.WINDOW_WIDTH / 2) - int(temp_window_w / 2)
temp_window_y: int = int(constants.WINDOW_HEIGHT / 2) - int(temp_window_h / 2)
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


def temp_window_input_handle_finish(state: State, text: str) -> None:
    # parse and update state var
    try:
        val = float(text)
        if val == 0:
            raise Exception()
        state.room_temp = val
    except Exception:
        state.room_temp = None
        return

    # diable and hide temp window
    temp_window.disable()  # type: ignore[no-untyped-call]
    temp_window.hide()


#
# main loop
#


# clock
clock: Clock = pygame.Clock()

while state.running:
    #
    # temporal values
    #

    # time in seconds since last frame
    time_delta: float = clock.tick(constants.FPS) / 1000.0

    #
    # event-based updates
    #

    for event in pygame.event.get():
        # handle events manually
        match event.type:
            # quit app
            case pygame.QUIT:
                state.running = False

            # keypress
            case pygame.KEYDOWN:
                keydown_key: int = event.key
                match keydown_key:
                    # quit
                    case pygame.K_ESCAPE:
                        state.running = False
                    # increase speed
                    case pygame.K_w:
                        state.speed = min(
                            state.speed + constants.SPEED_STEP, constants.MAX_SPEED
                        )
                    # decrease speed
                    case pygame.K_s:
                        state.speed = max(
                            state.speed - constants.SPEED_STEP, constants.MIN_SPEED
                        )
                    # fire
                    case pygame.K_f if not state.data_needed:
                        stage.enqueue_fire_command(state.fire_duration)
                        now = time.time()

                        # update state
                        state.data_needed = True
                        state.flash_start_time = now
                        state.last_fire_time = now
                        state.last_fire_duration = state.fire_duration

                        # enable buttons
                        data_buttons_enable()

                    # scan grid
                    case pygame.K_m if not stage.is_busy():
                        stage.scan_grid(state.grid_size)
                        state.flash_start_time = time.time()

                    # skip data
                    case pygame.K_p:
                        state.data_needed = False
                        state.last_fire_time = None
                        state.last_fire_duration = None

                        # disable buttons
                        data_buttons_disable()

                    # move
                    case key if key in constants.SINGLE_MOVEMENT_MAP:
                        state.direction = constants.SINGLE_MOVEMENT_MAP[key]
                    # move with arrows, should this be removed?
                    case key if key in constants.CONTINUOUS_MOVEMENT_MAP:
                        state.direction = constants.CONTINUOUS_MOVEMENT_MAP[key]

            # key un-press
            case pygame.KEYUP:
                keyup_key: int = event.key
                if (
                    keyup_key in constants.SINGLE_MOVEMENT_MAP
                    and state.direction is constants.SINGLE_MOVEMENT_MAP[keyup_key]
                ) or (
                    keyup_key in constants.CONTINUOUS_MOVEMENT_MAP
                    and state.direction is constants.CONTINUOUS_MOVEMENT_MAP[keyup_key]
                ):
                    state.direction = None

            # mouse click
            case pygame.MOUSEBUTTONDOWN:
                event_pos: tuple[int, int] = event.pos
                event_button: int = event.button
                over_video_frame = video_frame_collidepoint(event_pos[0], event_pos[1])
                match event_button:
                    # left mouse button, in place_marker mode, and over video
                    case 1 if state.place_marker and over_video_frame:
                        video_frame_place_marker(state, event_pos[0], event_pos[1])

            # text entry complete (enter is pressed when selected)
            case pygame_gui.UI_TEXT_ENTRY_FINISHED:
                event_ui_element: UITextEntryLine = event.ui_element
                event_text: str = event.text
                match event_ui_element:
                    case e if e is data_id_input:
                        data_id_input_handle_finish(state, event_text)
                    case e if e is data_strain_input:
                        data_strain_input_handle_finish(state, event_text)
                    case e if e is fire_duration_input:
                        fire_duration_input_handle_finish(state, event_text)
                    case e if e is grid_size_input:
                        grid_size_input_handle_finish(state, event_text)
                    case e if e is move_duration_input:
                        move_duration_input_handle_finish(state, event_text)
                    case e if e is temp_window_input:
                        temp_window_input_handle_finish(state, event_text)

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
    status_box_update(state)

    # update data recording status box text
    data_status_box_update(state)

    # update flash box
    flash_panel_update(state)

    # do movement
    if state.direction is not None:
        stage.enqueue_move_command(state.speed, state.direction, state.move_duration)
        print(f"moving {state.direction}")

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
