# std
from dataclasses import dataclass

# relative
from .._layout import Layout


@dataclass(frozen=True, kw_only=True)
class StartLayout(Layout): ...
