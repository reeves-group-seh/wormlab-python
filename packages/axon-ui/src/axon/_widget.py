# std
from typing import override

# extern
import pygame_gui

# relative
from ._component import Component
from ._util import RectLike


class Widget(Component):
    """
    A `Component` that deals with `pygame_gui` elements directly.

    It owns a root `pygame_gui.core.UIContainer`, created in `__init__`, which
    must hold every element the widget builds. Child tracking, the `on_*` hooks,
    and `bind` all behave as they do on `Component`.

    ## The root container

    - **Container.** Children are built into the root, so their coordinates are
      local to the widget.
    - **Anchor target.** The root is a `pygame_gui` element, so other widgets
      can anchor to it.
    - **Lifetime.** Killing the root kills every element inside it.

    The root draws nothing. For a background or border, build a
    `pygame_gui.elements.UIPanel` inside it. A container clips its children to
    its own rectangle, so a root smaller than its contents truncates them.

    ## Building a widget

    Call `super().__init__` first, then build elements into `self.element`:

    ```python
    class SpinBox(Widget):
        def __init__(
            self,
            manager: pygame_gui.UIManager,
            container: pygame_gui.core.IContainerLikeInterface | None,
            rect: RectLike,
        ) -> None:
            super().__init__(manager, container, rect)

            rect = as_rect(rect)
            self._dec = pygame_gui.elements.UIButton(
                relative_rect=(0, 0, rect.height, rect.height),
                text="<",
                manager=manager,
                container=self.element,
            )
    ```

    ## Anchoring

    Anchoring to another widget's `element` replaces hand-computed offsets; the
    `rect` is then measured from the target's edge:

    ```python
    label = Label(manager, panel, (0, 0, 200, 30), text="Speed")
    spin = SpinBox(
        manager,
        panel,
        (0, 4, 200, 30),  # 4px below the label
        anchors={"top_target": label.element},
    )
    ```

    ## Teardown

    `on_destroy` kills the root, releasing the widget's elements automatically.
    A subclass that overrides it must call `super().on_destroy()` or the
    elements will outlive the widget.
    """

    # instance vars
    _root: pygame_gui.core.UIContainer

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: RectLike,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        """
        Create the widget's root container.

        Subclasses must call this before building any child elements, and must
        build those elements into `element`.

        :param manager: The `pygame_gui.UIManager` that owns this widget's
            elements.
        :param container: The container holding the root, or `None` to place it
            at the root of the manager.
        :param rect: The widget's position and size, relative to `container`,
            or an anchored element's edge.
        :param anchors: A `pygame_gui` anchors mapping controlling how the root
            is positioned. See `pygame_gui`'s documentation on how anchors work
            for more info.
        """
        self._root = pygame_gui.core.UIContainer(
            relative_rect=rect,
            manager=manager,
            container=container,
            anchors=anchors,
        )

    @property
    def element(self) -> pygame_gui.core.UIContainer:
        """
        This widget's root container.

        Pass it as the `container` of any element the widget builds, or as a
        `*_target` anchor to position another widget relative to this one.
        """
        return self._root

    @override
    def on_destroy(self) -> None:
        """
        Kill the root container, and with it every element inside the widget.

        Called by `Component.destroy` after children have been destroyed and all
        `bind` subscriptions released. A subclass that overrides this must call
        `super().on_destroy()`, or the widget's elements will outlive it.
        """
        self._root.kill()  # type: ignore[no-untyped-call]
