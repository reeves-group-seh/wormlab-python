# module imports
import struct
import time

# item imports
from collections import deque
from dataclasses import dataclass
from serial import Serial

# local module imports
import constants

# local item imports
from direction import Direction


@dataclass
class SerialBridge:
    """
    Class dealing with communication to the arduino.
    """

    #
    # attributes
    #

    _ser: Serial
    """
    Serial connection to arduino.
    """

    _command_queue: deque[_SerialCommand]
    """
    Queue of commands to write to the arduino.
    """

    _current_command: _SerialCommandExecution | None
    """
    The currently executing command.
    """

    #
    # constructors
    #

    def __init__(self) -> None:
        """
        Open a serial connection to the arduino.

        :raises SerialException:
            If the connection to the serial port cannot be opened.
        """

        # create serial connection, raising SerialException on failure
        self._ser = Serial(
            port=constants.SERIAL_PORT,
            baudrate=constants.SERIAL_BAUDRATE,
            timeout=constants.SERIAL_CONNECTION_TIMEOUT,
        )

        # create empty queue
        self._command_queue = deque([])

        # specify current command as None
        self._current_command = None

    #
    # getter / basic state methods
    #

    def is_busy(self) -> bool:
        """
        Whether a command is currently executing.

        :rtype: bool
        :return:
            `True` if a command is executing and `False` otherwise.
        """

        return self._current_command is not None

    def close(self) -> None:
        """
        Close the serial connection. The object is no longer valid after this
        method is called.
        """

        self._ser.close()

    #
    # immediate write methods
    #

    def _write_command(self, command: _SerialCommand) -> None:
        """
        Send a command to the serial connection immediatly. This will overwrite
        `_current_command` without checking to ensure it is `None`.

        :type command: SerialCommand
        :param command:
            The command to write.
        """

        # write command packet & update state to match
        self._ser.write(command.to_packet())
        self._current_command = _SerialCommandExecution(command)

    #
    # queue methods
    #

    def _enqueue_command(self, command: _SerialCommand) -> None:
        """
        Enqueue a command to be executed on a first-in-first-out basis.

        :type command: SerialCommand
        :param command:
            The command to eventually write.
        """

        self._command_queue.append(command)

    def enqueue_move_command(
        self, speed: float, direction: Direction, duration: float
    ) -> None:
        """
        Enqueue a move command to be executed on a first-in-first-out basis.

        :type speed: float
        :param speed:
            The speed in steps per second.

        :type direction: Direction
        :param direction:
            The direction to move the stage.

        :type duration: float
        :param duration:
            The duration in milliseconds for the stage to move.
        """

        self._enqueue_command(
            _SerialCommand.new_move_command(speed, direction, duration)
        )

    def enqueue_fire_command(self, duration: float) -> None:
        """
        Enqueue a fire command to be executed on a first-in-first-out basis.

        :type duration: float
        :param duration:
            The duration in milliseconds to fire the laser.
        """

        self._enqueue_command(_SerialCommand.new_fire_command(duration))

    def _dequeue_command(self) -> _SerialCommand | None:
        """
        Remove and return the next item from the command queue.

        :rtype: SerialCommand | None
        :return:
            The next command in the queue or `None` if the queue is empty.
        """

        try:
            return self._command_queue.popleft()
        except IndexError:
            return None

    #
    # render loop method
    #

    def update(self) -> None:
        """
        Update the command execution state. This should be called in a loop
        (the frame render loop) to keep executing commands in the queue.
        """

        # remove currenly executing command if complete
        if (
            self._current_command is not None
            and self._current_command.execution_time_elapsed()
        ):
            self._current_command = None

        # if not executing, write the next command in queue
        if self._current_command is None:
            cmd: _SerialCommand | None = self._dequeue_command()
            if cmd is not None:
                self._write_command(cmd)

    def scan_grid(
        self,
        n: int,
        speed: float = constants.DEFAULT_GRID_SCAN_SPEED,
        move_duration: float = constants.DEFAULT_GRID_SCAN_MOVE_DURATION,
        fire_duration: float = constants.DEFAULT_GRID_SCAN_FIRE_DURATION,
    ) -> None:
        """
        Move over an n by n grid, firing the laser in each position.

        :type n: int
        :param n:
            The size of the square grid.

        :type speed: float
        :param speed:
            The speed at which movement commands should be preformed
            in steps per second. This value along with the `move_duration`
            determine the distance between firings.

        :type move_duration: float
        :param move_duration:
            The movement duration in milliseconds between two adjacent
            positions. This value, along with the `speed`, determine the
            distance between firings.

        :type fire_duration: float
        :param fire_duration:
            The duration in milliseconds to fire the laser.
        """

        # start at top left, scan left to right, move left back to first column,
        # then down to the next row and repeat
        for row in range(n):
            # move right across columns of row
            for col in range(n):
                # fire at current position
                self.enqueue_fire_command(fire_duration)

                # move right if not last column
                if col < n - 1:
                    self.enqueue_move_command(speed, Direction.RIGHT, move_duration)

            # move left back to first col of row
            for col in range(n - 1):
                # move left
                self.enqueue_move_command(speed, Direction.LEFT, move_duration)

            # move down if not last row
            if row < n - 1:
                self.enqueue_move_command(speed, Direction.UP, move_duration)

        # move up to start after scanning
        for row in range(n - 1):
            self.enqueue_move_command(speed, Direction.DOWN, move_duration)


class DummySerialBridge(SerialBridge):
    """
    Placeholder `SerialBridge` that does nothing. Good for testing the UI
    without a serial connection.
    """

    def __init__(self) -> None:
        pass

    def is_busy(self) -> bool:
        return False

    def close(self) -> None:
        pass

    def enqueue_move_command(
        self, speed: float, direction: Direction, duration: float
    ) -> None:
        pass

    def enqueue_fire_command(self, duration: float) -> None:
        pass

    def update(self) -> None:
        pass

    def scan_grid(
        self,
        n: int,
        speed: float = constants.DEFAULT_GRID_SCAN_SPEED,
        move_duration: float = constants.DEFAULT_GRID_SCAN_MOVE_DURATION,
        fire_duration: float = constants.DEFAULT_GRID_SCAN_FIRE_DURATION,
    ) -> None:
        pass


@dataclass
class _SerialCommandExecution:
    """
    Data class containing info about the execution of a command.
    """

    #
    # attributes
    #

    start_time: float
    """
    Timestamp (from `time.time()`) of when the command was written to the serial
    port.
    """

    command: _SerialCommand
    """
    Command being executed.
    """

    #
    # constructors
    #

    def __init__(self, command: _SerialCommand) -> None:
        """
        Initialize the command with the current time.

        :type command: SerialCommand
        :param command:
            The command being executed.
        """

        self.start_time = time.time()
        self.command = command

    #
    # instance methods
    #

    def execution_time_elapsed(self) -> bool:
        """
        Whether the command's theoretical execution time has elapsed since when
        the command was first executed.

        :rtype: bool
        :return:
            Returns `True` if the execution time has elapsed and `False`
            otherwise.
        """

        return (time.time() - self.start_time) >= self.command.max_duration()


@dataclass
class _SerialCommand:
    """
    Data class containing info about a single command to send to the arduino.
    """

    #
    # data
    #

    speed: float
    """
    The speed in steps per second of a movement command.
    """

    direction: Direction
    """
    The direction of a movement command.
    """

    move_duration: float
    """
    The duration in milliseconds of a movement command.
    """

    fire_duration: float
    """
    The duration in milliseconds of a fire command.
    """

    #
    # constructor methods
    #

    @staticmethod
    def new_move_command(
        speed: float, direction: Direction, duration: float
    ) -> _SerialCommand:
        """
        Create a new SerialCommand that moves the stage.

        :type speed: float
        :param speed:
            The speed in steps per second.

        :type direction: Direction
        :param direction:
            The direction to move the stage.

        :type duration: float
        :param duration:
            The duration in milliseconds for the stage to move.

        :rtype: SerialCommand
        :return:
            A new "movement" command.
        """
        return _SerialCommand(
            speed=speed,
            direction=direction,
            move_duration=duration,
            fire_duration=0,
        )

    @staticmethod
    def new_fire_command(duration: float) -> _SerialCommand:
        """
        Create a new SerialCommand that fires the laser.

        :type duration: float
        :param duration:
            The duration in milliseconds to fire the laser.

        :rtype: SerialCommand
        :return:
            A new "fire" command.
        """
        return _SerialCommand(
            speed=0.0,
            direction=Direction.DEFAULT,
            move_duration=0.0,
            fire_duration=duration,
        )

    #
    # instance methods
    #

    def max_duration(self) -> float:
        """
        The theorietical runtime of the command in seconds, or the max of the
        move and fire durations.

        :rtype: float
        :return:
            The max duration in seconds.
        """
        return max(self.move_duration, self.fire_duration) / 1000.0

    def to_packet(self) -> bytes:
        """
        Create a binary packet from this command.

        :rtype: bytes
        :return:
            The binary packet.
        """

        # create a packet of 5 float values
        packet: bytes = struct.pack(
            "fffff",
            -1.0,  # header
            self.speed,
            float(self.direction),
            self.move_duration,
            self.fire_duration,
        )
        return packet
