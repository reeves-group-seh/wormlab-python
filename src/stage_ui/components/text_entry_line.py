# std
from typing import override

# relative
from ._text_entry_line_base import BaseTextEntryLineComponent


class TextEntryLineComponent[T](BaseTextEntryLineComponent[T]):
    @override
    def _on_parse_error(self) -> None:
        pass
