# std
import dataclasses
import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# local
from shooter.types import (
    FilterNumber,
    LaserFire,
    RadiusColor,
    WormBehavior,
    WormResponse,
)


class EventType(StrEnum):
    # general
    SESSION_START = "session_start"
    COMMENT = "comment"

    # fires
    DATA_FIRE = "data_fire"
    DESTROY_FIRE = "destroy_fire"
    SKIPPED_FIRE = "skipped_fire"

    # behavior
    BEHAVIOR = "behavior"


@dataclass(kw_only=True, frozen=True)
class DataRow:
    # event data
    event_version: str = "2.0"
    event_time: dt.datetime
    event_type: EventType

    # room info
    room_temp: float
    room_humidity: float

    # general fire data
    fire_duration: float | None

    # data fire data
    data_fire_radius_color: RadiusColor | None
    data_fire_filter_number: FilterNumber | None
    data_fire_worm_strain: str | None
    data_fire_worm_id: str | None
    data_fire_response: WormResponse | None

    # behavior data
    behavior: WormBehavior | None

    # multi-use comment
    comment: str | None

    @staticmethod
    def fields() -> list[str]:
        return [key.name for key in dataclasses.fields(DataRow)]

    def as_dict(self) -> dict[str, Any]:
        dict = dataclasses.asdict(self)
        dict["event_time"] = self.event_time.isoformat(timespec="seconds")

        return dict


class DataBackend(ABC):
    """
    ...
    """

    def open(
        self,
        data_dir: Path,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        Start a new data session.
        """

        # start time
        start_time = dt.datetime.now().astimezone()

        # open file & add start event
        self._open_file(data_dir / f"{start_time.strftime('%Y-%m-%dT%H%M%S')}.csv")
        self._add_row(
            DataRow(
                event_time=start_time,
                event_type=EventType.SESSION_START,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=None,
                data_fire_radius_color=None,
                data_fire_filter_number=None,
                data_fire_worm_strain=None,
                data_fire_worm_id=None,
                data_fire_response=None,
                behavior=None,
                comment=None,
            )
        )

    @abstractmethod
    def _open_file(self, data_file: Path) -> None:
        """
        Open and setup the data file itself.
        """

    @abstractmethod
    def _add_row(self, row: DataRow) -> None:
        """
        Record a given row of data.
        """

    def add_data_fire(
        self,
        *,
        fire: LaserFire,
        radius_color: RadiusColor,
        filter_number: FilterNumber,
        worm_strain: str,
        worm_id: str,
        response: WormResponse,
        comment: str,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        Record a fire with response.
        """

        self._add_row(
            DataRow(
                event_time=fire.time,
                event_type=EventType.DATA_FIRE,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=fire.duration,
                data_fire_radius_color=radius_color,
                data_fire_filter_number=filter_number,
                data_fire_worm_strain=worm_strain,
                data_fire_worm_id=worm_id,
                data_fire_response=response,
                behavior=None,
                comment=comment,
            )
        )

    def add_destroy_fire(
        self,
        fire: LaserFire,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        ...
        """

        self._add_row(
            DataRow(
                event_time=fire.time,
                event_type=EventType.DESTROY_FIRE,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=fire.duration,
                data_fire_radius_color=None,
                data_fire_filter_number=None,
                data_fire_worm_strain=None,
                data_fire_worm_id=None,
                data_fire_response=None,
                behavior=None,
                comment=None,
            )
        )

    def add_skipped_fire(
        self,
        fire: LaserFire,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        ...
        """

        self._add_row(
            DataRow(
                event_time=fire.time,
                event_type=EventType.SKIPPED_FIRE,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=fire.duration,
                data_fire_radius_color=None,
                data_fire_filter_number=None,
                data_fire_worm_strain=None,
                data_fire_worm_id=None,
                data_fire_response=None,
                behavior=None,
                comment=None,
            )
        )

    def add_comment(
        self,
        text: str,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        ...
        """

        self._add_row(
            DataRow(
                event_time=dt.datetime.now().astimezone(),
                event_type=EventType.COMMENT,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=None,
                data_fire_radius_color=None,
                data_fire_filter_number=None,
                data_fire_worm_strain=None,
                data_fire_worm_id=None,
                data_fire_response=None,
                behavior=None,
                comment=text,
            )
        )

    def add_behavior(
        self,
        behavior: WormBehavior,
        room_temp: float,
        room_humidity: float,
    ) -> None:
        """
        ...
        """

        self._add_row(
            DataRow(
                event_time=dt.datetime.now().astimezone(),
                event_type=EventType.BEHAVIOR,
                room_temp=room_temp,
                room_humidity=room_humidity,
                fire_duration=None,
                data_fire_radius_color=None,
                data_fire_filter_number=None,
                data_fire_worm_strain=None,
                data_fire_worm_id=None,
                data_fire_response=None,
                behavior=behavior,
                comment=None,
            )
        )
