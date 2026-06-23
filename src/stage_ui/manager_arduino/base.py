# std
from abc import ABC, abstractmethod


class ArduinoManager(ABC):
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
