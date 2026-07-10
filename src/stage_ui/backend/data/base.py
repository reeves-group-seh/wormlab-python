# std
import dataclasses
import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# local
from stage_ui.types import FilterNumber, LaserFire, RadiusColor, WormResponse


@dataclass(kw_only=True, frozen=True)
class DataRow:
    fire_time: dt.datetime
    fire_duration: float
    room_temp: float | None
    room_humidity: float | None
    radius_color: RadiusColor | None
    filter_number: FilterNumber | None
    worm_strain: str | None
    worm_id: str | None
    response: WormResponse | None
    notes: str | None

    @staticmethod
    def fields() -> list[str]:
        return [key.name for key in dataclasses.fields(DataRow)]

    def as_dict(self) -> dict[str, Any]:
        dict = dataclasses.asdict(self)
        dict["fire_time"] = self.fire_time.isoformat(timespec="seconds")
        return dict


class DataBackend(ABC):
    """"""

    @abstractmethod
    def open(self, data_file: Path) -> None:
        """
        Open the given data file for writing.
        """

    @abstractmethod
    def _add_row(self, row: DataRow) -> None:
        """
        Record a given row of data.
        """

    def add_data_entry(
        self,
        fire: LaserFire,
        room_temp: float,
        room_humidity: float,
        radius_color: RadiusColor,
        filter_number: FilterNumber,
        worm_strain: str,
        worm_id: str,
        response: WormResponse,
    ) -> None:
        """
        Record a fire with response.
        """
        self._add_row(
            DataRow(
                fire_time=fire.time,
                fire_duration=fire.duration,
                room_temp=room_temp,
                room_humidity=room_humidity,
                radius_color=radius_color,
                filter_number=filter_number,
                worm_strain=worm_strain,
                worm_id=worm_id,
                response=response,
                notes=None,
            )
        )

    def add_non_data_fire(
        self,
        fire: LaserFire,
        notes: str,
    ) -> None:
        """
        Record a fire not meant to be included in the data.
        """
        self._add_row(
            DataRow(
                fire_time=fire.time,
                fire_duration=fire.duration,
                room_temp=None,
                room_humidity=None,
                radius_color=None,
                filter_number=None,
                worm_strain=None,
                worm_id=None,
                response=None,
                notes=notes,
            )
        )
