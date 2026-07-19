# std
from collections.abc import Callable
from typing import ClassVar, override

# extern
import pygame
import pygame_gui

# local
import axon

# relative
from ._button import Button
from ._input import Input, InputStrict


class SpinBox[T](axon.Widget):
    """
    ...
    """

    # class variables
    _PADDING: ClassVar[int] = 2

    # instance variables
    _value: axon.Atom[T]
    _inc: Callable[[T], T]
    _dec: Callable[[T], T]
    _parse: Callable[[str], T]
    _format: Callable[[T], str]
    _input_valid_class_id: str | None
    _input_invalid_class_id: str | None
    _input_obj_id: str | None

    _input: Input[T]

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        value: axon.Atom[T],
        inc: Callable[[T], T],
        dec: Callable[[T], T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        inc_text: str = "+",
        dec_text: str = "-",
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        input_valid_class_id: str | None = None,
        input_invalid_class_id: str | None = "@axonkit_input_invalid",
        input_obj_id: str | None = None,
        buttons_class_id: str | None = None,
        buttons_obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # set values
        self._value = value
        self._inc = inc
        self._dec = dec
        self._parse = parse
        self._format = format
        self._input_valid_class_id = input_valid_class_id
        self._input_invalid_class_id = input_invalid_class_id
        self._input_obj_id = input_obj_id

        # calculate
        input_width = rect.width - ((2 * rect.height) + (2 * self._PADDING))

        # create (dispatches to the subclass factory)
        self._input = self._create_input(
            manager, pygame.Rect(0, 0, input_width, rect.height)
        )
        dec_button = Button(
            manager=manager,
            container=self.element,
            rect=pygame.Rect(self._PADDING, 0, rect.height, rect.height),
            text=dec_text,
            anchors={"left": "left", "left_target": self._input.element},
            on_click=self._dec_value,
            class_id=buttons_class_id,
            obj_id=buttons_obj_id,
        )
        Button(
            manager=manager,
            container=self.element,
            rect=pygame.Rect(self._PADDING, 0, rect.height, rect.height),
            text=inc_text,
            anchors={"left": "left", "left_target": dec_button.element},
            on_click=self._inc_value,
            class_id=buttons_class_id,
            obj_id=buttons_obj_id,
        )

    def _create_input(
        self,
        manager: pygame_gui.UIManager,
        rect: pygame.Rect,
    ) -> Input[T]:
        return Input(
            manager=manager,
            container=self.element,
            rect=rect,
            value=self._value,
            parse=self._parse,
            format=self._format,
            valid_class_id=self._input_valid_class_id,
            invalid_class_id=self._input_invalid_class_id,
            obj_id=self._input_obj_id,
        )

    def _inc_value(self) -> None:
        self._value.value = self._inc(self._value.value)

    def _dec_value(self) -> None:
        self._value.value = self._dec(self._value.value)


class SpinBoxStrict[T](SpinBox[T | None]):
    """
    ...
    """

    # instance variables
    _strict_parse: Callable[[str], T]
    _strict_format: Callable[[T], str]

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        value: axon.Atom[T | None],
        inc: Callable[[T], T],
        dec: Callable[[T], T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        inc_text: str = "+",
        dec_text: str = "-",
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        input_valid_class_id: str | None = None,
        input_invalid_class_id: str | None = "@axonkit_input_invalid",
        input_obj_id: str | None = None,
        buttons_class_id: str | None = None,
        buttons_obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # store strict parse / format
        self._strict_parse = parse
        self._strict_format = format

        # init parent
        super().__init__(
            manager=manager,
            container=container,
            rect=rect,
            value=value,
            inc=lambda v: None if v is None else inc(v),
            dec=lambda v: None if v is None else dec(v),
            parse=parse,
            format=lambda v: "" if v is None else format(v),
            inc_text=inc_text,
            dec_text=dec_text,
            anchors=anchors,
            input_valid_class_id=input_valid_class_id,
            input_invalid_class_id=input_invalid_class_id,
            input_obj_id=input_obj_id,
            buttons_class_id=buttons_class_id,
            buttons_obj_id=buttons_obj_id,
        )

    @override
    def _create_input(
        self,
        manager: pygame_gui.UIManager,
        rect: pygame.Rect,
    ) -> Input[T | None]:
        return InputStrict(
            manager=manager,
            container=self.element,
            rect=rect,
            value=self._value,
            parse=self._strict_parse,
            format=self._strict_format,
            valid_class_id=self._input_valid_class_id,
            invalid_class_id=self._input_invalid_class_id,
            obj_id=self._input_obj_id,
        )
