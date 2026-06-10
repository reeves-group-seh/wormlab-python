# local item imports
from stage_ui.context import Context
from stage_ui.screens import Screen


class HomeScreen(Screen):
    def __init__(self, ctx: Context) -> None:
        super().__init__(ctx)
