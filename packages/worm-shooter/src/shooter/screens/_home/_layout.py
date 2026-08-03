# std
from dataclasses import dataclass

# relative
from .._layout import Layout


@dataclass(frozen=True, kw_only=True)
class HomeLayout(Layout):
    stage_panel_w: int = 469
    """
    The width of the `StagePanel` component.
    """

    behavior_comment_box_h: int = 52
    """
    The height of the comment input box in the `BehaviorPanel`.
    """

    left_5_btn_pad_x: int = 5
    """
    Horizontal padding between the buttons in `BehaviorPanel` and `FirePanel`.
    This value is tied to the screen's left column width and panel padding. If
    these values change, this must be recomputed manually.
    """

    behavior_btn_h: int = 67
    """
    The height of the `BehaviorPanel` buttons.
    """

    fire_btn_w: int = 90
    """
    The width of each response button in the `FirePanel`. This value is tied to
    the screen's left column width and must be recomputed manually when that
    changes.
    """

    fire_btn_pad_x: int = 6
    """
    Horizontal padding between the buttons in `FirePanel`. This value is tied to
    `fire_btn_w` and the screen's left column width. If these values change,
    this must be recomputed manually.
    """

    def left_5_btn_w(self, panel_w: int) -> int:
        space = panel_w - ((2 * (self.border_pad)) + (4 * self.left_5_btn_pad_x))
        return space // 5
