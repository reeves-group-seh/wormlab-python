# item imports
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pandas import DataFrame
from pathlib import Path


@dataclass
class DataHandler:
    """
    Class for handling the creation and modification of datafiles.
    """

    _datafile: Path
    """
    File to create (if needed) and append to.
    """

    def __init__(self, datafile: Path) -> None:
        """
        Initialize a new object for handling the provided datafile.

        :type datafile: Path
        :param datafile: The datafile to create and store data in.
        """

        # set values
        self._datafile = datafile

        # create file
        if not self._datafile.is_file():
            df: DataFrame = DataFrame(
                {
                    "fire_time": [],
                    "fire_duration": [],
                    "worm_strain": [],
                    "worm_id": [],
                    "worm_response": [],
                    "room_temp": [],
                }
            )
            df.to_csv(self._datafile, index=False)

    def add_entry(
        self,
        fire_time: datetime,
        fire_duration: float,
        worm_strain: str,
        worm_id: str,
        worm_response: Response,
        room_temp: float,
    ) -> None:
        """
        Add a new entry to the datafile.

        :type fire_time: datetime
        :param fire_time:
            Time that the laser was fired.

        :type fire_duration: float
        :param fire_duration:
            Duration that the laser was fired for in milliseconds.

        :type worm_strain: str
        :param worm_strain:
            The strain of the recorded worm.

        :type worm_id: str
        :param worm_id:
            The unique identifier for the recorded worm.

        :type worm_response: Response
        :param response:
            The worm's response.

        :type room_temp: float
        :param room_temp:
            The temperature of the room in degrees celsius.
        """

        # create dataframe and append to datafile
        df: DataFrame = DataFrame(
            {
                "fire_time": [fire_time],
                "fire_duration": [fire_duration],
                "worm_strain": [worm_strain],
                "worm_id": [worm_id],
                "worm_response": [str(worm_response)],
                "room_temp": [room_temp],
            }
        )
        df.to_csv(self._datafile, mode="a", index=False, header=False)


class Response(Enum):
    """
    Enum representing the possible worm responses.
    """

    FULL = "F"
    PARTIAL = "P"
    ACKNOWLEDGE = "A"
    NO_RESPONSE = "N"

    def __str__(self) -> str:
        """
        Convert this enum value to a string.

        :rtype: str
        :return:
            The single-letter string representation of this response.
        """

        match self:
            case Response.FULL:
                return "F"
            case Response.PARTIAL:
                return "P"
            case Response.ACKNOWLEDGE:
                return "A"
            case Response.NO_RESPONSE:
                return "N"
