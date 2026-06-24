# std
from pathlib import Path
from typing import override

# pip
import pandas as pd

# relative
from .base import DataManager, DataRow


class PandasDataManager(DataManager):
    def __init__(self) -> None:
        self._data_file: Path | None = None

    @override
    def open(self, data_file: Path) -> None:
        self._data_file = data_file
        pd.DataFrame(
            {key: [] for key in DataRow.fields()},
        ).to_csv(
            data_file,
            index=False,
        )

    @override
    def _add_row(self, row: DataRow) -> None:
        pd.DataFrame(
            {key: [value] for key, value in row.as_dict().items()},
        ).to_csv(
            self._data_file,
            mode="a",
            index=False,
            header=False,
        )
