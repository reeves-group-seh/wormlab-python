# std
from pathlib import Path

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextBox

# local
from stage_ui.atom import Atom
from stage_ui.components import NO_MARGINS, Component


class InfoPanelComponent(Component):
    # constants
    W: int = 395
    H: int = 220

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        datafile: Path,
        status: Atom[str],
        room_temp: Atom[float],
        room_humidity: Atom[float],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.datafile = datafile
        self.status = status
        self.room_temp = room_temp
        self.room_humidity = room_humidity

        # bindings
        self.bind(status, self._render_top_info)
        self.bind(room_temp, self._render_top_info)
        self.bind(room_humidity, self._render_top_info)

        # unpack values
        x, y = pos

        # panel
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                container=container,
                margins=NO_MARGINS,
            )
        )

        # top info
        self.top_info = self.track(
            UITextBox(
                html_text="",
                relative_rect=(5, 5, self.W - 10, 160),
                manager=manager,
                container=panel,
                object_id="#info_top",
            )
        )
        self.top_info.disable()

        # bottom info
        bottom_info = self.track(
            UITextBox(
                html_text="Press <b>H</b> for help",
                relative_rect=(5, 165, self.W - 10, 50),
                manager=manager,
                container=panel,
                object_id="#info_bottom",
            )
        )
        bottom_info.disable()

        # do initial render
        self._render_top_info()

    def _render_top_info(self) -> None:
        # grab data
        top_info_dict = {
            "Status": self.status.value,
            "Datafile": self.datafile.name,
            "Temperature": f"{self.room_temp.value} \u2103",
            "Humidity": f"{self.room_humidity.value}%",
        }
        top_info_str = "<br/>".join(
            f"<b>{key}</b>: {val}" for key, val in top_info_dict.items()
        )

        # update text
        self.top_info.set_text(top_info_str)
