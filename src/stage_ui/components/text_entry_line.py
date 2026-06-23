# std
from typing import override

# local
from stage_ui.components._text_entry_line_base import BaseTextEntryLineComponent


class TextEntryLineComponent[T](BaseTextEntryLineComponent[T]):
    @override
    def on_parse_error(self) -> None:
        pass
