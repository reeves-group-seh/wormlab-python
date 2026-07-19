# extern
import pygame
import pygame_gui

# local
import axon


class Panel(axon.Widget):
    """
    ...
    """

    # instance variables
    _panel: pygame_gui.elements.UIPanel

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        class_id: str | None = "@axonkit_panel",
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

        # create
        self._panel = pygame_gui.elements.UIPanel(
            relative_rect=(0, 0, rect.width, rect.height),
            manager=manager,
            margins={"top": 0, "right": 0, "bottom": 0, "left": 0},
            container=self.element,
            object_id=object_id,
        )
