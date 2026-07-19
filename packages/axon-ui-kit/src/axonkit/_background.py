# extern
import pygame
import pygame_gui

# local
import axon


class Background(axon.Widget):
    """
    ...
    """

    # instance variables
    _panel: pygame_gui.elements.UIPanel

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        size: tuple[int, int],
        class_id: str | None = "@axonkit_background",
        obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, None, pygame.Rect(0, 0, size[0], size[1]), None)

        # derive inputs
        object_id = pygame_gui.core.ObjectID(
            object_id=obj_id,
            class_id=class_id,
        )

        # create
        self._panel = pygame_gui.elements.UIPanel(
            relative_rect=(0, 0, size[0], size[1]),
            manager=manager,
            margins={"top": 0, "right": 0, "bottom": 0, "left": 0},
            container=self.element,
            object_id=object_id,
        )
