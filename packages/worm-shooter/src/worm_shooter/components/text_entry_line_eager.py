# std
from collections.abc import Callable
from typing import override

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from worm_shooter.atom import Atom

# relative
from ._text_entry_line_base import BaseTextEntryLineComponent


class EagerTextEntryLineComponent[T](BaseTextEntryLineComponent[T | None]):
    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        value: Atom[T | None],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        valid_class_id: str | None = None,
        invalid_class_id: str = "@text_entry_line_invalid",
    ) -> None:
        # init parent
        super().__init__(
            manager=manager,
            container=container,
            pos=pos,
            w=w,
            value=value,
            parse=parse,
            format=lambda v: "" if v is None else format(v),
            valid_class_id=valid_class_id,
            invalid_class_id=invalid_class_id,
        )

    @override
    def _on_parse_error(self) -> None:
        self._value.value = None
