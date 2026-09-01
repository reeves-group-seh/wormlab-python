# std
import struct
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Thread
from typing import override

# pip
import serial
import serial.tools.list_ports

# local
import axon

# relative
from ._base import ArduinoAction, ArduinoBackend


class PySerialArduinoBackend(ArduinoBackend):
    _worker: _SerialWorker | None
    """
    Helper that handles the worker thread and writes binary packets to the
    arduino.
    """

    _action: _SerialAction
    """
    The current action to be given to the arduino.
    """

    _executing_action: axon.Atom[ArduinoAction]
    """
    The action currently being executed by the arduino worker.
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
    A factor determining how long to wait between writes to the arduino. A
    value of 1.0 indicates the program will wait for exactly the
    theroretical execution time of a command before sending another. A value
    of 2.0 indicates the program will wait for double this theroretical
    execution time, 0.5 will wait half, etc. To be safe, this value should
    be set to a value > 1.0.
    """

    def __init__(
        self,
        baudrate: int,
        timeout: float,
        sleep_factor: float,
    ) -> None:
        self._worker = None
        self._action = _SerialActionIdle()
        self._executing_action = axon.Atom(ArduinoAction.IDLE)
        self._baudrate = baudrate
        self._timeout = timeout
        self._sleep_factor = sleep_factor

    @override
    def open(self, port: str) -> None:
        self._worker = _SerialWorker(
            port,
            self._baudrate,
            self._timeout,
            self._sleep_factor,
        )

    @override
    def close(self) -> None:
        # no-op if closed
        if self._worker is None:
            return

        # kill worker
        self._worker.kill()
        self._worker = None
        self._action = _SerialActionIdle()

    @override
    def busy(self) -> bool:
        if self._worker is None:
            return False
        return (
            not isinstance(self._action, _SerialActionIdle)
            or not self._worker.queue_empty()
            or self._worker.current_action() is not ArduinoAction.IDLE
        )

    @override
    def action(self) -> axon.Atom[ArduinoAction]:
        return self._executing_action

    @override
    def stop(self) -> None:
        self._action = _SerialActionIdle()

    @override
    def move_left(self, speed: float, duration: float) -> None:
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.LEFT,
            duration=duration,
        )

    @override
    def move_right(self, speed: float, duration: float) -> None:
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.RIGHT,
            duration=duration,
        )

    @override
    def move_up(self, speed: float, duration: float) -> None:
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.UP,
            duration=duration,
        )

    @override
    def move_down(self, speed: float, duration: float) -> None:
        self._action = _SerialActionMove(
            speed=speed,
            direction=_Direction.DOWN,
            duration=duration,
        )

    @override
    def step_left(self, speed: float, duration: float) -> None:
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.LEFT,
            duration=duration,
        )

    @override
    def step_right(self, speed: float, duration: float) -> None:
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.RIGHT,
            duration=duration,
        )

    @override
    def step_up(self, speed: float, duration: float) -> None:
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.UP,
            duration=duration,
        )

    @override
    def step_down(self, speed: float, duration: float) -> None:
        self._action = _SerialActionStep(
            speed=speed,
            direction=_Direction.DOWN,
            duration=duration,
        )

    @override
    def fire(self, duration: float) -> None:
        self._action = _SerialActionFire(duration=duration)

    @override
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

        :param speed:
            Speed to move in steps per second.

        :param move_duration:
            Duration to to move for in milliseconds between fires.

        :param fire_duration:
            Duration to fire the laser for.
        """

        self._action = _SerialActionGrid(
            n=n,
            move_speed=move_speed,
            move_duration=move_duration,
            fire_duration=fire_duration,
        )

    @override
    def update(self) -> None:
        """
        Continue to communicate with the arduino. This should be called on every
        frame.
        """
        # no worker, nothing to do
        if self._worker is None:
            return

        # mirror the worker's currently executing action
        self._executing_action.value = self._worker.current_action()

        # only send new commands once the worker has drained its queue
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

    @override
    def ports(self) -> list[str]:
        return [port.device for port in serial.tools.list_ports.comports()]


class _Direction(Enum):
    """
    Direction of stage movement. The value of each variant is the value sent to
    the arduino.
    """

    # directions
    LEFT = 0.0
    RIGHT = 1.0
    DOWN = 2.0
    UP = 3.0

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

    @override
    def run(self, worker: _SerialWorker) -> None:
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

    @override
    def run(self, worker: _SerialWorker) -> None:
        action: ArduinoAction
        match self.direction:
            case _Direction.LEFT | _Direction.DEFAULT:
                action = ArduinoAction.MOVE_LEFT
            case _Direction.RIGHT:
                action = ArduinoAction.MOVE_RIGHT
            case _Direction.UP:
                action = ArduinoAction.MOVE_UP
            case _Direction.DOWN:
                action = ArduinoAction.MOVE_DOWN

        worker.enqueue_move(self.speed, self.direction, self.duration, action)


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

    @override
    def run(self, worker: _SerialWorker) -> None:
        action: ArduinoAction
        match self.direction:
            case _Direction.LEFT | _Direction.DEFAULT:
                action = ArduinoAction.STEP_LEFT
            case _Direction.RIGHT:
                action = ArduinoAction.STEP_RIGHT
            case _Direction.UP:
                action = ArduinoAction.STEP_UP
            case _Direction.DOWN:
                action = ArduinoAction.STEP_DOWN

        worker.enqueue_move(self.speed, self.direction, self.duration, action)


@dataclass(kw_only=True, frozen=True)
class _SerialActionFire(_SerialAction):
    """
    An action representing a fire of the laser.
    """

    duration: float
    """
    Duration to fire for in milliseconds.
    """

    @override
    def run(self, worker: _SerialWorker) -> None:
        worker.enqueue_fire(
            self.duration,
            ArduinoAction.FIRE,
        )


@dataclass(kw_only=True, frozen=True)
class _SerialActionGrid(_SerialAction):
    """
    An action representing the step-and-shoot functionality.
    """

    n: int
    """
    Size of the NxN grid.
    """

    move_speed: float
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

    @override
    def run(self, worker: _SerialWorker) -> None:
        # loop over number of rows in grid
        for row in range(self.n):
            # loop over number of columns in grid
            for col in range(self.n):
                # enqueue move right if not first col in row
                if col > 0:
                    worker.enqueue_move(
                        self.move_speed,
                        _Direction.RIGHT,
                        self.move_duration,
                        ArduinoAction.GRID,
                    )
                # fire laser at current point
                worker.enqueue_fire(self.fire_duration, ArduinoAction.GRID)

            # if row is not the last, move left back to first col, then
            # down one to next row
            if row < self.n - 1:
                # move left until back to col 1
                for _ in range(self.n - 1):
                    worker.enqueue_move(
                        self.move_speed,
                        _Direction.LEFT,
                        self.move_duration,
                        ArduinoAction.GRID,
                    )
                # move down (?) 1. everything was labeled down but int
                # was 3, so i changed const to indicate up?
                worker.enqueue_move(
                    self.move_speed,
                    _Direction.UP,
                    self.move_duration,
                    ArduinoAction.GRID,
                )

        # move up to top row. should this also move to left? also this
        # was again 2 but labeled everywhere as up?
        for _ in range(self.n - 1):
            worker.enqueue_move(
                self.move_speed,
                _Direction.DOWN,
                self.move_duration,
                ArduinoAction.GRID,
            )


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

    _current_action: ArduinoAction
    """
    The action currently executing.
    """

    _thread: Thread
    """
    The worker thread dealing with writing to the serial port.
    """

    def __init__(
        self,
        port: str,
        bauderate: int,
        timeout: float,
        sleep_factor: float,
    ) -> None:
        self._port = port
        self._baudrate = bauderate
        self._timeout = timeout
        self._sleep_factor = sleep_factor
        self._queue = Queue()
        self._current_action = ArduinoAction.IDLE
        self._thread = Thread(target=self._thread_loop, daemon=True)
        self._thread.start()

    def queue_empty(self) -> bool:
        """
        Check whether the command queue is empty.
        """
        return self._queue.empty()

    def current_action(self) -> ArduinoAction:
        """
        The action the worker is currently executing.
        """
        return self._current_action

    def enqueue_fire(
        self,
        duration: float,
        action: ArduinoAction,
    ) -> None:
        """
        Add a fire command to the queue.
        """
        self._queue.put(_SerialCommand.new_fire_command(duration, action))

    def enqueue_move(
        self,
        speed: float,
        direction: _Direction,
        duration: float,
        action: ArduinoAction,
    ) -> None:
        """
        Add a move command to the queue.
        """
        self._queue.put(
            _SerialCommand.new_move_command(
                speed,
                direction,
                duration,
                action,
            )
        )

    def kill(self) -> None:
        """
        Send a signal to close serial connection and kill the created thread.
        """
        self._queue.put(None)
        self._thread.join()

    def _thread_loop(self) -> None:
        """
        Loop for the thread to run continuously.
        """
        with serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        ) as ser:
            while True:
                command = self._queue.get()
                if command is None:
                    break
                self._current_action = command.action
                ser.write(command.to_packet())
                time.sleep((command.max_duration() / 1000.0) * self._sleep_factor)
                if self._queue.empty():
                    self._current_action = ArduinoAction.IDLE


@dataclass(kw_only=True)
class _SerialCommand:
    """
    A command sent to the arduino as a binary packet.
    """

    move_speed: float
    """
    Speed to move in steps per second.
    """

    move_direction: _Direction
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

    action: ArduinoAction
    """
    The action this command represents.
    """

    @staticmethod
    def new_move_command(
        speed: float,
        direction: _Direction,
        duration: float,
        action: ArduinoAction,
    ) -> _SerialCommand:
        """
        Create a new command that moves the stage.
        """
        return _SerialCommand(
            move_speed=speed,
            move_direction=direction,
            move_duration=duration,
            fire_duration=0.0,
            action=action,
        )

    @staticmethod
    def new_fire_command(
        duration: float,
        action: ArduinoAction,
    ) -> _SerialCommand:
        """
        Create a new command that fires the laser.
        """
        return _SerialCommand(
            move_speed=0.0,
            move_direction=_Direction.DEFAULT,
            move_duration=0.0,
            fire_duration=duration,
            action=action,
        )

    def max_duration(self) -> float:
        """
        The theorietical runtime of the command in milliseconds (the max of the
        move and fire durations).
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
            self.move_speed,
            self.move_direction.value,
            self.move_duration,
            self.fire_duration,
        )
        return packet
