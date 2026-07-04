# std
import signal
import sys

# pip
import pygame

# local
import stage_ui
from stage_ui.app_config import AppConfig
from stage_ui.app_context import AppContext
from stage_ui.app_router import AppRouter
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager


class App:
    # instance variables
    _ctx: AppContext
    _window_surf: pygame.Surface
    _router: AppRouter
    _clock: pygame.Clock
    _dt: float

    def __init__(
        self,
        cfg: AppConfig,
        arduino_man: ArduinoManager,
        camera_man: CameraManager,
        data_man: DataManager,
    ) -> None:
        pygame.init()
        pygame.display.set_caption(stage_ui.APP_NAME)

        # init values
        self._ctx = AppContext(
            cfg=cfg,
            arduino_man=arduino_man,
            camera_man=camera_man,
            data_man=data_man,
        )
        self._window_surf = pygame.display.set_mode(cfg.WINDOW_SIZE)
        self._router = AppRouter(self._ctx)
        self._clock = pygame.Clock()
        self._dt: float = float("inf")

    def run(self) -> None:
        # register ctrl-c
        signal.signal(
            signal.SIGINT,
            lambda _s, _f: pygame.event.post(pygame.Event(pygame.QUIT)),
        )

        # render loop
        while True:
            # update time delta
            self._dt = self._clock.tick(self._ctx.cfg.FPS) / 1000.0

            # handle events
            for event in pygame.event.get():
                # match on types
                if event.type == pygame.QUIT:
                    print("StageUI: shutting down")
                    self._ctx.destroy()
                    pygame.quit()
                    sys.exit(0)

                # event handlers
                self._router.process_event(event)

            # update
            self._router.update(self._dt)
            self._ctx.arduino_man.update()

            # draw ui
            self._router.draw_ui(self._window_surf)

            # update display
            pygame.display.flip()
