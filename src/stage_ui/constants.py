# module imports
import pygame
import time

# item imports
from datetime import datetime

# local item imports
from direction import Direction


TESTING: bool = True
"""
Whether the app should be run in "testing" mode.
"""

WINDOW_NAME: str = "Stage Controller"
"""
Application name.
"""

DATA_FILE: str = f"data/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv"
"""
Name of the CSV datafile to create & write to.
"""

PROG_START_TIME: float = time.time()
"""
Time (from `time.time()`) that the program started at.
"""

CAMERA_INDEX: int = 3 if not TESTING else 0
"""
OpenCV video capture camera index.
"""

FPS: int = 60
"""
Max number of frames per second to render at.
"""

#
# serial
#

SERIAL_PORT: str = "COM3"
"""
Port to communicate with the arduino on.
"""

SERIAL_BAUDRATE: int = 115200
"""
Baudrate to communicate with the arduino at.
"""

SERIAL_CONNECTION_TIMEOUT: float = 0.1
"""
The timeout for the serial connection.
"""

#
# movement speed
#

SPEED_STEP: float = 10.0
"""
Value to increment and decrement speed by.
"""

MIN_SPEED: float = 10.0
"""
Minimum stage movement speed in steps per second.
"""

MAX_SPEED: float = 1000.0
"""
Maximum stage movement speed in steps per second.
"""

DEFAULT_SPEED: float = 100.0
"""
Default stage movement speed in steps per second.
"""

#
# move duration
#

MIN_MOVE_DURATION: float = 1.0
"""
Mimimum stage move duration in milliseconds.
"""

MAX_MOVE_DURATION: float = 5000.0
"""
Maximum stage move duration in milliseconds.
"""

DEFAULT_MOVE_DURATION: float = 100.0
"""
Default stage move duration in milliseconds.
"""

#
# fire duration
#

MIN_FIRE_DURATION: float = 1.0
"""
Mimimum laser fire duration in milliseconds.
"""

MAX_FIRE_DURATION: float = 10000.0
"""
Maximum laser fire duration in milliseconds.
"""

DEFAULT_FIRE_DURATION: float = 200.0
"""
Default laser fire duration in milliseconds.
"""

#
# test grid
#

MIN_GRID_SIZE: int = 1
"""
Minumum size of the square test grid.
"""

MAX_GRID_SIZE: int = 20
"""
Maximum size of the square test grid.
"""

DEFAULT_GRID_SIZE: int = 3
"""
Default size of the square test grid.
"""

DEFAULT_GRID_SCAN_SPEED: float = 100.0
"""
Default speed in steps per second of movement commands in a grid scan.
"""

DEFAULT_GRID_SCAN_MOVE_DURATION: float = 10.0
"""
Default duration in milliseconds of movement commands in a grid scan.
"""

DEFAULT_GRID_SCAN_FIRE_DURATION: float = 1000.0
"""
Default duration in milliseconds of fire commands in a grid scan.
"""

#
# ui sizing
#

WINDOW_WIDTH: int = 1000
"""
Width of the application window.
"""

WINDOW_HEIGHT: int = 650
"""
Height of the application window.
"""

WINDOW_SEP: int = 20
"""
Amount of padding between main panels.
"""

WINDOW_PANEL_SEP: int = 10
"""
Amount of padding between sub-panels.
"""

#
# key mappings
#

SINGLE_MOVEMENT_MAP: dict[int, Direction] = {
    pygame.K_h: Direction.LEFT,
    pygame.K_k: Direction.RIGHT,
    pygame.K_u: Direction.UP,
    pygame.K_j: Direction.DOWN,
}
"""
Key-direction mappings for single movements.
"""

CONTINUOUS_MOVEMENT_MAP: dict[int, Direction] = {
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
}
"""
Key-direction mappings for continuous movements.
"""
