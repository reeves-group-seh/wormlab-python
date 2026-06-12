# std
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# pip
from pandas import DataFrame

# local
from stage_ui.types import FilterNumber, RadiusColor, WormResponse


@dataclass(kw_only=True)
class DataManager:
    """
    Class for handling the creation and modification of datafiles.
    """

    _datafile: Path
    """
    File to create (if needed) and append to.
    """

    @staticmethod
    def new(datafile: Path) -> DataManager:
        """
        Initialize a new object for handling the provided datafile.

        :param datafile:
            The file to create and store data in.
        """

        # create object
        return DataManager(_datafile=datafile)

    def check_and_create_file(self) -> None:
        if not self._datafile.is_file():
            _DataRow.blank_data_frame().to_csv(self._datafile, index=False)

    def add_entry(
        self,
        fire_time: datetime,
        room_temp: float,
        radius_color: RadiusColor,
        filter_num: FilterNumber,
        worm_strain: str,
        worm_id: int,
        fire_duration: float,
        response: WormResponse,
    ) -> None:
        """
        Add a new entry to the datafile.
        """

        # ensure file exists
        self.check_and_create_file()

        # write new row
        _DataRow(
            fire_time=fire_time,
            room_temp=room_temp,
            radius_color=radius_color,
            filter_num=filter_num,
            worm_strain=worm_strain,
            worm_id=worm_id,
            fire_duration=fire_duration,
            response=response,
        ).to_data_frame().to_csv(self._datafile, mode="a", index=False, header=False)


@dataclass(kw_only=True, frozen=True)
class _DataRow:
    """
    A single row in the datafile.
    """

    # id
    fire_time: datetime

    # session info
    room_temp: float

    # subsession info
    radius_color: RadiusColor
    filter_num: FilterNumber
    worm_strain: str
    worm_id: int

    # shot info
    fire_duration: float
    response: WormResponse

    @staticmethod
    def blank_data_frame() -> DataFrame:
        return DataFrame({key.name: [] for key in dataclasses.fields(_DataRow)})

    def to_data_frame(self) -> DataFrame:
        return DataFrame({key: [val] for key, val in dataclasses.asdict(self).items()})
