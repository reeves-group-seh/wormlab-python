# item imports
from typing import Protocol

# local item imports
from stage_ui.manager_serial.hardware import HardwareSerialManager
from stage_ui.manager_serial.mock import MockSerialManager

# public api
__all__ = [
    # top level
    "SerialManager",
    # re-exports
    "HardwareSerialManager",
    "MockSerialManager",
]


class SerialManager(Protocol):
    def stop(self) -> None:
        """
        Make the stage go idle. The arduino will complete the last action before
        stopping (i.e. this command is not immediate).
        """

    def move_left(self, speed: float, duration: float) -> None:
        """
        Move the stage left continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def move_right(self, speed: float, duration: float) -> None:
        """
        Move the stage right continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def move_up(self, speed: float, duration: float) -> None:
        """
        Move the stage up continuously. This is not stopped until a call to the
        `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def move_down(self, speed: float, duration: float) -> None:
        """
        Move the stage down continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def step_left(self, speed: float, duration: float) -> None:
        """
        Move left a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def step_right(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move right a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def step_up(self, speed: float, duration: float) -> None:
        """
        Move up a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def step_down(self, speed: float, duration: float) -> None:
        """
        Move down a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """

    def fire(self, duration: float) -> None:
        """
        Fire the laser.

        :param duration:
            The time in milliseconds to fire the laser.
        """

    def grid(
        self,
        n: int,
        speed: float,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        """
        Execute the step-and-shoot functionality.

        :param n:
            Size of the NxN grid.

        :param speed:
            Speed to move in steps per second.

        :param move_duration:
            Duration to to move for in milliseconds between fires.

        :param fire_duration:
            Duration to fire the laser for.
        """

    def update(self) -> None:
        """
        Continue to communicate with the arduino. This should be called on every
        frame.
        """
