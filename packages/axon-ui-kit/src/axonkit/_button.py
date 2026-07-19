# std
from collections.abc import Callable

# extern
import pygame
import pygame_gui

# local
import axon


class Button(axon.Widget):
    """
    ...
    """

    # instance variables
    _button: pygame_gui.elements.UIButton

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        text: str,
        on_click: Callable[[], None] | None = None,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        class_id: str | None = None,
        obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # derive inputs
        object_id = pygame_gui.core.ObjectID(
            object_id=obj_id,
            class_id=class_id,
        )

        # set values
        ...

        # create
        self._button = pygame_gui.elements.UIButton(
            relative_rect=(0, 0, rect.width, rect.height),
            text=text,
            manager=manager,
            container=self.element,
            object_id=object_id,
        )
        self._button.bind(pygame_gui.UI_BUTTON_PRESSED, on_click)

        # bind
        ...

    def enable(self) -> None:
        """
        ...
        """
        self._button.enable()  # type: ignore[no-untyped-call]

    def disable(self) -> None:
        """
        ...
        """
        self._button.disable()  # type: ignore[no-untyped-call]
