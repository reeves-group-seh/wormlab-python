# module imports
import struct

# item imports
from dataclasses import dataclass
from typing import Self

# local item imports
from direction import Direction


@dataclass
class SerialCommand:
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
    ) -> SerialCommand:
        """
        Create a new SerialCommand that moves the stage.

        :param speed: The speed in steps per second.
        :type speed: float
        :param direction: The direction to move the stage.
        :type direction: Direction
        :param duration: The duration in milliseconds for the stage to move.
        :type duration: float

        :return: A new "movement" command.
        :rtype: SerialCommand
        """
        return SerialCommand(
            speed=speed,
            direction=direction,
            move_duration=duration,
            fire_duration=0,
        )

    @staticmethod
    def new_fire_command(duration: float) -> SerialCommand:
        """
        Create a new SerialCommand that fires the laser.

        :param duration: The duration in milliseconds to fire the laser.
        :type duration: float

        :return: A new "fire" command.
        :rtype: SerialCommand
        """
        return SerialCommand(
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
        The theorietical runtime of the command, or the max of the move and fire
        durations.

        :return: The max duration in seconds.
        :rtype: float
        """
        return max(self.move_duration, self.fire_duration) / 1000.0

    def to_packet(self) -> bytes:
        """
        Create a binary packet from this command.

        :return: The binary packet.
        :rtype: bytes
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
