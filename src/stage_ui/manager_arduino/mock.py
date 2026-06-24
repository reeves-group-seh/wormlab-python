# std
from typing import override

# relative
from .base import ArduinoManager


class MockArduinoManager(ArduinoManager):
    # constants
    LOG_PREFIX = "MockArduinoManager"

    def __init__(self) -> None:
        self._port: str | None = None

    @override
    def open(self, port: str) -> None:
        self._port = port
        print(f"{self.LOG_PREFIX}: opened at port '{port}'")

    @override
    def close(self) -> None:
        # already closed
        if self._port is None:
            print(f"{self.LOG_PREFIX}: attempted to close non-open port")
            return

        # close
        print(f"{self.LOG_PREFIX}: closed at port '{self._port}'")
        self._port = None

    @override
    def stop(self) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(f"{self.LOG_PREFIX}: received 'stop' command")

    @override
    def move_left(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'move_left' command, speed={speed}, duration={duration}"
        )

    @override
    def move_right(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'move_right' command, speed={speed}, duration={duration}"
        )

    @override
    def move_up(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'move_up' command, speed={speed}, duration={duration}"
        )

    @override
    def move_down(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'move_down' command, speed={speed}, duration={duration}"
        )

    @override
    def step_left(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'step_left' command, speed={speed}, duration={duration}"
        )

    @override
    def step_right(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'step_right' command, speed={speed}, duration={duration}"
        )

    @override
    def step_up(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'step_up' command, speed={speed}, duration={duration}"
        )

    @override
    def step_down(self, speed: float, duration: float) -> None:
        if self._port is None:
            raise Exception("resource has not been opened")

        print(
            f"{self.LOG_PREFIX}: received 'step_down' command, speed={speed}, duration={duration}"
        )

    @override
    def fire(self, duration: float) -> None:
        print(f"{self.LOG_PREFIX}: received 'fire' command, duration={duration}")

    @override
    def grid(
        self,
        n: int,
        move_speed: float,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        print(
            f"{self.LOG_PREFIX}: received 'grid' command, n={n}, move_speed={move_speed}, move_duration={move_duration}, fire_duration={fire_duration}"
        )

    @override
    def update(self) -> None:
        pass

    @override
    def ports(self) -> list[str]:
        """
        Get a listing of all available serial ports.
        """
        return ["COM3", "COM4"]
