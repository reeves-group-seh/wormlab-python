# constants
LOG_PREFIX = "MockSerialManager"


class MockSerialManager:
    def stop(self) -> None:
        print(f"{LOG_PREFIX}: received 'stop' command")

    def move_left(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'move_left' command, speed={speed}, duration={duration}"
        )

    def move_right(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'move_right' command, speed={speed}, duration={duration}"
        )

    def move_up(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'move_up' command, speed={speed}, duration={duration}"
        )

    def move_down(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'move_down' command, speed={speed}, duration={duration}"
        )

    def step_left(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'step_left' command, speed={speed}, duration={duration}"
        )

    def step_right(
        self,
        speed: float,
        duration: float,
    ) -> None:
        print(
            f"{LOG_PREFIX}: received 'step_right' command, speed={speed}, duration={duration}"
        )

    def step_up(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'step_up' command, speed={speed}, duration={duration}"
        )

    def step_down(self, speed: float, duration: float) -> None:
        print(
            f"{LOG_PREFIX}: received 'step_down' command, speed={speed}, duration={duration}"
        )

    def fire(self, duration: float) -> None:
        print(f"{LOG_PREFIX}: received 'fire' command, duration={duration}")

    def grid(
        self,
        n: int,
        speed: float,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        print(
            f"{LOG_PREFIX}: received 'grid' command, n={n}, speed={speed}, move_duration={move_duration}, fire_duration={fire_duration}"
        )

    def update(self) -> None: ...
