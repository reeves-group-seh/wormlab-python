# item imports
from collections import deque
from serial import Serial, SerialException

# local item imports
from serial_command import SerialCommand


# constants
PORT: str = "COM3"
BAUDRATE: int = 115200
CONNECTION_TIMEOUT: float = 0.1


class SerialBridge:
    """
    Class dealing with communication to the arduino.
    """

    def __init__(self, silent_fail: bool = False) -> None:
        """
        Open a serial connection to the arduino.

        :param silent_fail: Whether to catch a `SerialException` if connection
        to the arduino fails.
        :type silent_fail: bool

        :raises SerialException: If the connection to the serial port cannot be
        opened. This should not be raised if `silent_fail` is set to `True`
        """

        # empty serial connection
        self.ser: Serial | None = None

        # command queue
        self.command_queue: deque[SerialCommand] = deque([])

        # whether blocking (?) commands are executing
        self.is_executing: bool = False

        # start time of executing cmd
        self.current_command_start_time: float | None = None

        # time the executing cmd should take (s)
        self.current_command_duration: float = 0.0

        # try to create serial connection
        try:
            self.ser = Serial(port=PORT, baudrate=BAUDRATE, timeout=CONNECTION_TIMEOUT)
        except SerialException as e:
            if silent_fail:
                self.ser = None
            else:
                raise e

    # send packet via serial connection immediately
    def send_command_immediate(self, command: Command) -> None:
        """
        Send a command to arduino immediately. This is a blocking operation.

        :param command: The command to execute.
        """

        # check for connection
        if not self.ser:
            return

        # write command packet to the serial port
        self.ser.write(command.packet())

        # update internal state to indicate a command is executing
        self.is_executing = True
        self.current_command_start_time = time.time()
        self.current_command_duration = command.max_duration()

    # enqueue a command. is this ever used properly?
    def queue_command(
        self,
        speed: float,
        direction: Direction,
        move_duration: float,
        fire_duration: float,
    ) -> None:
        """Queue a command for non-blocking execution"""

        command: Command = Command(
            speed,
            direction,
            move_duration,
            fire_duration,
        )

        # add to the queue
        self.command_queue.put(command)

    # check and update internal state each frame
    def update(self) -> None:
        """Update command execution state - call this every frame"""

        # if command is executing (with start time present) and command is
        # complete (theoretical execution time has elapsed) set is_executing to
        # False and current_command_start_time to None
        if self.is_executing and self.current_command_start_time:
            if (
                time.time() - self.current_command_start_time
                >= self.current_command_duration
            ):
                self.is_executing = False
                self.current_command_start_time = None

        # if not executing, try to execute a command in queue
        if not self.is_executing:
            try:
                command = self.command_queue.get_nowait()
                self.send_command_immediate(command)
            except Empty:
                pass

    # repeatedly fire laser in a square grid pattern
    def scan_grid(self, n: int, speed: float = 100.0, step_time: float = 10.0) -> None:
        """Queue commands for grid scanning pattern"""

        # loop over number of rows in grid
        for row in range(n):
            # loop over number of columns in grid
            for col in range(n):
                # enqueue move right if not first col in row
                if col > 0:
                    self.queue_command(speed, Direction.RIGHT, step_time, 0)
                # fire laser at current point
                self.queue_command(0, Direction.DEFAULT, 0, 1000)

            # if row is not the last, move left back to first col, then
            # down one to next row
            if row < n - 1:
                # move left until back to col 1
                for _ in range(n - 1):
                    self.queue_command(speed, Direction.LEFT, step_time, 0)
                # move down (?) 1. everything was labeled down but int was 3, so
                # i changed const to indicate up?
                self.queue_command(speed, Direction.UP, step_time, 0)

        # move up to top row. should this also move to left? also this was again
        # 2 but labeled everywhere as up ?
        for _ in range(n - 1):
            self.queue_command(speed, Direction.DOWN, step_time, 0)

    # return if is_executing or if queue is not empty.
    def is_busy(self) -> bool:
        """Check if controller is busy executing commands"""

        return self.is_executing or not self.command_queue.empty()
