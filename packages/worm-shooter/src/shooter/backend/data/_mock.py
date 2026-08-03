from pathlib import Path
from typing import ClassVar, override

from ._base import DataBackend, DataRow


class MockDataBackend(DataBackend):
    # class constants
    _LOG_PREFIX: ClassVar[str] = "MockDataBackend"

    # instance variables
    _data_file: Path | None

    def __init__(self) -> None:
        self._data_file = None

    @override
    def _open_file(self, data_file: Path) -> None:
        self._data_file = data_file
        print(f"{self._LOG_PREFIX}: opened file '{data_file}'")

    @override
    def _add_row(self, row: DataRow) -> None:
        if self._data_file is None:
            raise Exception("resource has not been opened")

        kv_pairs = ", ".join(
            [f"{key}='{value}'" for key, value in row.as_dict().items()]
        )
        print(f"{self._LOG_PREFIX}: adding row, {kv_pairs}")
