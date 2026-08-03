# std
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Layout:
    """
    Layout lengths for screens, plus some helpers for doing layout math.

    Only *leaf* values live here as fields; every composite length (panel sizes,
    column widths, the vertical fill panels) is derived from these by the
    panels, so editing one token cascades everywhere.
    """

    # window (supplied from AppConfig)

    window_w: int
    window_h: int

    # panel border/shadow

    border: int = 5
    """
    Padding between two panels.
    """

    # padding

    border_pad: int = 10
    """
    Gap between a panel border and the first/last element in it.
    """

    border_label_pad_y: int = 5
    """
    Gap between a the top of a panel and a label.
    """

    label_input_pad_y: int = 5
    """
    Gap between an label and input.
    """

    label_label_pad_y: int = 5
    """
    Gap between two labels.
    """

    input_label_pad_y: int = 5
    """
    Gap between an input and label.
    """

    input_input_pad_y: int = 10
    """
    Gap between two inputs.
    """

    column_pad_x: int = 5
    """
    Gap between two inner-panel columns.
    """

    # video feed

    video_w: int = 600
    """
    Width of just the 3:2 video feed.
    """

    video_h: int = 400
    """
    Height of just the 3:2 video feed.
    """

    # cross-screen elements

    panel_heading_h: int = 20
    """
    The height of `shooter.components.PanelHeading` components.
    """

    status_bar_h: int = 27
    """
    The height of the status bar shown on the bottom of the screen.
    """

    label_h: int = 20
    """
    The height of `axonkit.Label` components.
    """

    input_h: int = 28
    """
    The height of `axonkit.Input` (and similar text entry line) components.
    """

    @staticmethod
    def stack(*parts: int) -> int:
        """
        Total height of a vertical or horizontal run of stacked segments
        (headers, labels, inputs, buttons, and the padding between them).

        Summing named segments lets a panel's height read as the list of things
        it contains, instead of a single hand-computed literal.

        :param *parts: The integer length measurements.
        :returns: The total length of all elements combined.
        """
        return sum(parts)
