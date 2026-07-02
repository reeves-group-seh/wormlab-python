# std
from typing import ClassVar, override

# local
from stage_ui.atom import Atom

# relative
from .base import ArduinoAction, ArduinoManager


class MockArduinoManager(ArduinoManager):
    # constants
    _LOG_PREFIX: ClassVar[str] = "MockArduinoManager"

    # instance variables
    _port: str | None
    _action: Atom[ArduinoAction]

    def __init__(self) -> None:
        self._port = None
        self._action = Atom(ArduinoAction.IDLE)

    @override
    def open(self, port: str) -> None:
        self._port = port
        print(f"{self._LOG_PREFIX}: opened at port '{port}'")

    @override
    def close(self) -> None:
        # already closed
        if self._port is None:
            print(f"{self._LOG_PREFIX}: attempted to close non-open port")
            return

        # close
        print(f"{self._LOG_PREFIX}: closed at port '{self._port}'")
        self._port = None

    @override
    def action(self) -> Atom[ArduinoAction]:
        return self._action

    @override
    def stop(self) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        self._action.value = ArduinoAction.IDLE
        print(f"{self._LOG_PREFIX}: received 'stop' command")

    @override
    def move_left(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        self._action.value = ArduinoAction.MOVE_LEFT
        print(
            f"{self._LOG_PREFIX}: received 'move_left' command, speed={speed}, duration={duration}"
        )

    @override
    def move_right(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        self._action.value = ArduinoAction.MOVE_RIGHT
        print(
            f"{self._LOG_PREFIX}: received 'move_right' command, speed={speed}, duration={duration}"
        )

    @override
    def move_up(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        self._action.value = ArduinoAction.MOVE_UP
        print(
            f"{self._LOG_PREFIX}: received 'move_up' command, speed={speed}, duration={duration}"
        )

    @override
    def move_down(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        self._action.value = ArduinoAction.MOVE_DOWN
        print(
            f"{self._LOG_PREFIX}: received 'move_down' command, speed={speed}, duration={duration}"
        )

    @override
    def step_left(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self._LOG_PREFIX}: received 'step_left' command, speed={speed}, duration={duration}"
        )

    @override
    def step_right(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self._LOG_PREFIX}: received 'step_right' command, speed={speed}, duration={duration}"
        )

    @override
    def step_up(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self._LOG_PREFIX}: received 'step_up' command, speed={speed}, duration={duration}"
        )

    @override
    def step_down(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self._LOG_PREFIX}: received 'step_down' command, speed={speed}, duration={duration}"
        )

    @override
    def fire(self, duration: float) -> None:
        print(f"{self._LOG_PREFIX}: received 'fire' command, duration={duration}")

    @override
    def grid(
        self,
        n: int,
        move_speed: float,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        print(
            f"{self._LOG_PREFIX}: received 'grid' command, n={n}, move_speed={move_speed}, move_duration={move_duration}, fire_duration={fire_duration}"
        )

    @override
    def update(self) -> None:
        pass

    @override
    def ports(self) -> list[str]:
        return ["COM3", "COM4"]
