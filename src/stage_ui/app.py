# std
import signal
import sys

# pip
import pygame

# local
import stage_ui
from stage_ui.config import Config
from stage_ui.context import Context
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager
from stage_ui.manager_screen import ScreenManager


class App:
    # instance variables
    _ctx: Context
    _window_surf: pygame.Surface
    _screen_man: ScreenManager
    _clock: pygame.Clock
    _dt: float

    def __init__(
        self,
        cfg: Config,
        arduino_man: ArduinoManager,
        camera_man: CameraManager,
        data_man: DataManager,
    ) -> None:
        pygame.init()
        pygame.display.set_caption(stage_ui.APP_NAME)

        # init values
        self._ctx = Context(
            cfg=cfg,
            arduino_man=arduino_man,
            camera_man=camera_man,
            data_man=data_man,
        )
        self._window_surf = pygame.display.set_mode(cfg.WINDOW_SIZE)
        self._screen_man = ScreenManager(self._ctx)
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
                self._screen_man.process_event(event)

            # update
            self._screen_man.update(self._dt)
            self._ctx.arduino_man.update()

            # draw ui
            self._screen_man.draw_ui(self._window_surf)

            # update display
            pygame.display.flip()
