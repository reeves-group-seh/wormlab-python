"""
Module that handles communication with the arduino.
"""

# module imports
import struct
import time

# item imports
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue
from serial import Serial
from threading import Thread


@dataclass(kw_only=True)
class SerialManager:
    """
    Bridge that orchestrates communication to the ardunio.
    """

    _worker: _SerialWorker
    """
    Helper that handles the worker thread and writes binary packets to the
    arduino.
    """

    _action: _SerialAction
    """
    The current high-level action being preformed.
    """

    _default_grid_speed: float
    """
    The default speed for movement commands when using step-and-shoot.
    """

    _default_grid_move_duration: float
    """
    The default duration of move commands when using step-and-shoot.
    """

    _default_grid_fire_duration: float
    """
    The default duration of fire commands when using step-and-shoot.
    """

    @staticmethod
    def new(
        port: str,
        baudrate: int,
        timeout: float,
        sleep_factor: float,
        default_grid_speed: float,
        default_grid_move_duration: float,
        default_grid_fire_duration: float,
    ) -> SerialManager:
        """
        Create a new `SerialBridge` with the given serial configuration.

        :param port:
            The port to connect to the arduino on.

        :param baudrate:
            The rate in which to communicate with the arduino.

        :param timeout:
            The time in seconds to timeout the connection to the arduino.

        :param sleep_factor:
            A factor determining how long to wait between writes to the arduino.
            A value of 1.0 indicates the program will wait for exactly the
            theroretical execution time of a command before sending another.
            A value of 2.0 indicates the program will wait for double this
            theroretical execution time, 0.5 will wait half, etc. To be safe,
            this value should be set to a value > 1.0.

        :param default_grid_speed:
            The default speed for movement commands when using step-and-shoot.

        :param default_grid_move_duration:
            The default duration of move commands when using step-and-shoot.

        :param default_grid_fire_duration:
            The default duration of fire commands when using step-and-shoot.
        """
        return SerialManager(
            _worker=_SerialWorker.new(port, baudrate, timeout, sleep_factor),
            _action=_SerialActionIdle(),
            _default_grid_speed=default_grid_speed,
            _default_grid_move_duration=default_grid_move_duration,
            _default_grid_fire_duration=default_grid_fire_duration,
        )

    def stop(self) -> None:
        """
        Make the stage go idle. The arduino will complete the last action before
        stopping (i.e. this command is not immediate).
        """
        self._action = _SerialActionIdle()

    def move_left(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move the stage left continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.LEFT,
            duration=duration,
        )

    def move_right(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move the stage right continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.RIGHT,
            duration=duration,
        )

    def move_up(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move the stage up continuously. This is not stopped until a call to the
        `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.UP,
            duration=duration,
        )

    def move_down(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move the stage down continuously. This is not stopped until a call to
        the `stop` method is made.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.DOWN,
            duration=duration,
        )

    def step_left(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move left a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.LEFT,
            duration=duration,
        )

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
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.RIGHT,
            duration=duration,
        )

    def step_up(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move up a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.UP,
            duration=duration,
        )

    def step_down(
        self,
        speed: float,
        duration: float,
    ) -> None:
        """
        Move down a single step.

        :param speed:
            The speed in steps per second to move at.

        :param duration:
            The duration in milliseconds to move.
        """
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.DOWN,
            duration=duration,
        )

    def fire(
        self,
        duration: float,
    ) -> None:
        """
        Fire the laser.

        :param duration:
            The time in milliseconds to fire the laser.
        """
        self._action = _SerialActionFire(duration=duration)

    def grid(
        self,
        n: int,
        speed: float | None = None,
        move_duration: float | None = None,
        fire_duration: float | None = None,
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
        speed = speed if speed is not None else self._default_grid_speed
        move_duration = (
            move_duration
            if move_duration is not None
            else self._default_grid_move_duration
        )
        fire_duration = (
            fire_duration
            if fire_duration is not None
            else self._default_grid_fire_duration
        )

        self._action = _SerialActionGrid(
            n=n,
            speed=speed,
            move_duration=move_duration,
            fire_duration=fire_duration,
        )

    def update(
        self,
    ) -> None:
        """
        Continue to communicate with the arduino. This should be called on every
        frame.
        """
        # only update if worker is not executing
        if not self._worker.queue_empty():
            return

        # send command(s) based on action
        match self._action:
            case _SerialActionIdle():
                pass
            case _SerialActionMove():
                self._action.run(self._worker)
            case _SerialActionStep() | _SerialActionFire() | _SerialActionGrid():
                self._action.run(self._worker)
                self._action = _SerialActionIdle()


class _Direction(Enum):
    """
    Direction of stage movement. The value of each variant is the value sent to
    the arduino.
    """

    # directions
    LEFT = 0.0
    RIGHT = 1.0
    DOWN = 2.0  # away (up)
    UP = 3.0  # towards

    # default
    DEFAULT = LEFT


class _SerialAction(ABC):
    """
    Abstract class describing all high-level actions that the serial bridge can
    execute.
    """

    @abstractmethod
    def run(self, worker: _SerialWorker) -> None:
        """
        Execute the action by enqueuing commands to the given worker.
        """
        raise NotImplementedError


@dataclass(kw_only=True, frozen=True)
class _SerialActionIdle(_SerialAction):
    """
    An action representing doing nothing and sending no commands to the worker.
    """

    def run(self, _: _SerialWorker) -> None:
        pass


@dataclass(kw_only=True, frozen=True)
class _SerialActionMove(_SerialAction):
    """
    An action representing a continuous movement.
    """

    speed: float
    """
    Speed to move in steps per second.
    """

    direction: _Direction
    """
    Direction to move.
    """

    duration: float
    """
    Duration to move for in milliseconds.
    """

    def run(self, worker: _SerialWorker) -> None:
        worker.enqueue_move(self.speed, self.direction, self.duration)


@dataclass(kw_only=True, frozen=True)
class _SerialActionStep(_SerialAction):
    """
    An action representing a single movement.
    """

    speed: float
    """
    Speed to move in steps per second.
    """

    direction: _Direction
    """
    Direction to move.
    """

    duration: float
    """
    Duration to move for in milliseconds.
    """

    def run(self, worker: _SerialWorker) -> None:
        worker.enqueue_move(self.speed, self.direction, self.duration)


@dataclass(kw_only=True, frozen=True)
class _SerialActionFire(_SerialAction):
    """
    An action representing a fire of the laser.
    """

    duration: float
    """
    Duration to fire for in milliseconds.
    """

    def run(self, worker: _SerialWorker) -> None:
        worker.enqueue_fire(self.duration)


@dataclass(kw_only=True, frozen=True)
class _SerialActionGrid(_SerialAction):
    """
    An action representing the step-and-shoot functionality.
    """

    n: int
    """
    Size of the NxN grid.
    """

    speed: float
    """
    The speed to move in steps per second.
    """

    move_duration: float
    """
    The duration to to move for in milliseconds between fires.
    """

    fire_duration: float
    """
    The duration to fire the laser for.
    """

    def run(self, worker: _SerialWorker) -> None:
        # loop over number of rows in grid
        for row in range(self.n):
            # loop over number of columns in grid
            for col in range(self.n):
                # enqueue move right if not first col in row
                if col > 0:
                    worker.enqueue_move(
                        self.speed,
                        _Direction.RIGHT,
                        self.move_duration,
                    )
                # fire laser at current point
                worker.enqueue_fire(self.fire_duration)

            # if row is not the last, move left back to first col, then
            # down one to next row
            if row < self.n - 1:
                # move left until back to col 1
                for _ in range(self.n - 1):
                    worker.enqueue_move(
                        self.speed,
                        _Direction.LEFT,
                        self.move_duration,
                    )
                # move down (?) 1. everything was labeled down but int
                # was 3, so i changed const to indicate up?
                worker.enqueue_move(self.speed, _Direction.UP, self.move_duration)

        # move up to top row. should this also move to left? also this
        # was again 2 but labeled everywhere as up?
        for _ in range(self.n - 1):
            worker.enqueue_move(
                self.speed,
                _Direction.DOWN,
                self.move_duration,
            )


@dataclass(kw_only=True)
class _SerialWorker:
    """
    Worker that deals with creating a thread for serial communication and
    sending binary packets to it.
    """

    _port: str
    """
    Port to communicate to the arduino on.
    """

    _baudrate: int
    """
    The rate in which to communicate with the arduino.
    """

    _timeout: float
    """
    The time in seconds to timeout the connection to the arduino.
    """

    _sleep_factor: float
    """
    A factor determining how long to wait between writes to the arduino. A value
    of 1.0 indicates the program will wait for exactly the theroretical
    execution time of a command before sending another. A value of 2.0 indicates
    the program will wait for double this theroretical execution time, 0.5 will
    wait half, etc. To be safe, this value should be set to a value > 1.0.
    """

    _queue: Queue[_SerialCommand | None]
    """
    Queue of commands for the arduino to execute.
    """

    _thread: Thread = field(init=False)
    """
    The worker thread dealing with writing to the serial port.
    """

    def __post_init__(self) -> None:
        self._thread = Thread(target=self._thread_loop, daemon=True)
        self._thread.start()

    @staticmethod
    def new(
        port: str,
        baudrate: int,
        timeout: float,
        sleep_factor: float,
    ) -> _SerialWorker:
        """
        Create a new worker with the given config.
        """
        return _SerialWorker(
            _port=port,
            _baudrate=baudrate,
            _timeout=timeout,
            _sleep_factor=sleep_factor,
            _queue=Queue(),
        )

    def queue_empty(self) -> bool:
        """
        Check whether the command queue is empty.
        """
        return self._queue.empty()

    def enqueue_fire(self, duration: float) -> None:
        """
        Add a fire command to the queue.
        """
        self._queue.put(_SerialCommand.new_fire_command(duration))

    def enqueue_move(
        self,
        speed: float,
        direction: _Direction,
        duration: float,
    ) -> None:
        """
        Add a move command to the queue.
        """
        self._queue.put(_SerialCommand.new_move_command(speed, direction, duration))

    def _thread_loop(self) -> None:
        """
        Loop for the thread to run continuously.
        """
        with Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        ) as ser:
            while True:
                command = self._queue.get()
                if command is None:
                    break
                ser.write(command.to_packet())
                time.sleep((command.max_duration() / 1000.0) * self._sleep_factor)


@dataclass(kw_only=True)
class _SerialCommand:
    """
    A command sent to the arduino as a binary packet.
    """

    speed: float
    """
    Speed to move in steps per second.
    """

    direction: _Direction
    """
    Direction to move.
    """

    move_duration: float
    """
    Duration to move for in milliseconds.
    """

    fire_duration: float
    """
    Duration to fire for in milliseconds.
    """

    @staticmethod
    def new_move_command(
        speed: float,
        direction: _Direction,
        duration: float,
    ) -> _SerialCommand:
        """
        Create a new command that moves the stage.
        """
        return _SerialCommand(
            speed=speed,
            direction=direction,
            move_duration=duration,
            fire_duration=0.0,
        )

    @staticmethod
    def new_fire_command(duration: float) -> _SerialCommand:
        """
        Create a new command that fires the laser.
        """
        return _SerialCommand(
            speed=0.0,
            direction=_Direction.DEFAULT,
            move_duration=0.0,
            fire_duration=duration,
        )

    def max_duration(self) -> float:
        """
        The theorietical runtime of the command in seconds (the max of the move
        and fire durations).
        """
        return max(self.move_duration, self.fire_duration)

    def to_packet(self) -> bytes:
        """
        Create a binary packet from this command.
        """
        # create a packet of 5 float values
        packet: bytes = struct.pack(
            "fffff",
            -1.0,  # header ?
            self.speed,
            self.direction.value,
            self.move_duration,
            self.fire_duration,
        )
        return packet
