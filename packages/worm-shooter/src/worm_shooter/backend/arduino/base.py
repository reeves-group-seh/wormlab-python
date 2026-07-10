# std
import enum
from abc import ABC, abstractmethod
from enum import Enum
from typing import override

# local
from worm_shooter.atom import Atom


class ArduinoAction(Enum):
    """"""

    IDLE = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    STEP_LEFT = enum.auto()
    STEP_RIGHT = enum.auto()
    STEP_UP = enum.auto()
    STEP_DOWN = enum.auto()
    FIRE = enum.auto()
    GRID = enum.auto()

    @override
    def __str__(self) -> str:
        match self:
            case ArduinoAction.IDLE:
                return "Idle"
            case ArduinoAction.MOVE_LEFT:
                return "Move Left"
            case ArduinoAction.MOVE_RIGHT:
                return "Move Right"
            case ArduinoAction.MOVE_UP:
                return "Move Up"
            case ArduinoAction.MOVE_DOWN:
                return "Move Down"
            case ArduinoAction.STEP_LEFT:
                return "Step Left"
            case ArduinoAction.STEP_RIGHT:
                return "Step Right"
            case ArduinoAction.STEP_UP:
                return "Step Up"
            case ArduinoAction.STEP_DOWN:
                return "Step Down"
            case ArduinoAction.FIRE:
                return "Fire"
            case ArduinoAction.GRID:
                return "Grid"


class ArduinoBackend(ABC):
    """
    Bridge that handles communication to the ardunio.
    """

    @abstractmethod
    def open(self, port: str) -> None:
        """
        Open the serial connection at the given port.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the serial connection, if one exists, otherwise a no-op.
        """

    @abstractmethod
    def action(self) -> Atom[ArduinoAction]:
        """
        The action currently being executed.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Make the stage go idle. The arduino will complete the last action before
        stopping (i.e. this command is not immediate).
        """

    @abstractmethod
    def move_left(self, speed: float, duration: float) -> None:
        """
        Move the stage left continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def move_right(self, speed: float, duration: float) -> None:
        """
        Move the stage right continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def move_up(self, speed: float, duration: float) -> None:
        """
        Move the stage up continuously. This is not stopped until a call to the
        `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def move_down(self, speed: float, duration: float) -> None:
        """
        Move the stage down continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def step_left(self, speed: float, duration: float) -> None:
        """
        Move left a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def step_right(self, speed: float, duration: float) -> None:
        """
        Move right a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def step_up(self, speed: float, duration: float) -> None:
        """
        Move up a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def step_down(self, speed: float, duration: float) -> None:
        """
        Move down a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    @abstractmethod
    def fire(self, duration: float) -> None:
        """
        Fire the laser.

        :param duration:
            The time in milliseconds to fire the laser.
        """

    @abstractmethod
    def grid(
        self,
        n: int,
        move_speed: float,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        """
        Execute the step-and-shoot functionality.

        :param n:
            Size of the NxN grid.

        :param move_speed:
            Speed to move in steps per second.

        :param move_duration:
            Duration to to move for in milliseconds between fires.

        :param fire_duration:
            Duration to fire the laser for.
        """

    @abstractmethod
    def update(self) -> None:
        """
        Continue to communicate with the arduino. This should be called on every
        frame.
        """

    @abstractmethod
    def ports(self) -> list[str]:
        """
        Get a listing of all available serial ports.
        """
