# std
from typing import override

# local
import axon
import shooter
from shooter.backend import ArduinoBackend, CameraBackend, DataBackend
from shooter.screens import HomeScreen, ScreenId, StartScreen

# relative
from ._config import AppConfig
from ._context import AppContext


class App(axon.App[ScreenId]):
    """
    ...
    """

    # instance vars
    _ctx: AppContext

    def __init__(
        self,
        cfg: AppConfig,
        arduino: ArduinoBackend,
        camera: CameraBackend,
        data: DataBackend,
    ) -> None:
        """
        ...
        """

        # set values
        self._ctx = AppContext(
            cfg=cfg,
            arduino=arduino,
            camera=camera,
            data=data,
        )

        # parent
        super().__init__(
            app_name=shooter.APP_NAME,
            window_size=cfg.WINDOW_SIZE,
            screen_factories={
                ScreenId.HOME: lambda: HomeScreen(self._ctx),
                ScreenId.START: lambda: StartScreen(self._ctx),
            },
            initial_screen=ScreenId.START,
            fps=cfg.FPS,
        )

    @override
    def on_update(self, dt: float) -> None:
        self._ctx.arduino.update()

    @override
    def on_destroy(self) -> None:
        self._ctx.destroy()
