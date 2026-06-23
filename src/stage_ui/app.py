# std
import signal

# pip
import pygame
from pygame import Clock, Surface

# local
from stage_ui.config import Config
from stage_ui.context import Context, GlobalState
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager
from stage_ui.manager_screen import ScreenManager
from stage_ui.manager_serial import SerialManager


class App:
    def __init__(
        self,
        cfg: Config,
        camera_man: CameraManager,
        data_man: DataManager,
        serial_man: SerialManager,
    ) -> None:
        pygame.init()
        pygame.display.set_caption(cfg.APP_NAME)

        # init values
        self.ctx: Context = Context(
            cfg=cfg,
            camera_man=camera_man,
            data_man=data_man,
            serial_man=serial_man,
            state=GlobalState.new(),
        )
        self.window_surf: Surface = pygame.display.set_mode(
            (cfg.WINDOW_W, cfg.WINDOW_H)
        )
        self.screen_man: ScreenManager = ScreenManager(self.ctx)
        self.clock: Clock = Clock()
        self.running: bool = True
        self.dt: float = float("inf")

    def run(self) -> None:
        # register ctrl-c
        signal.signal(
            signal.SIGINT,
            lambda _s, _f: pygame.event.post(pygame.event.Event(pygame.QUIT)),
        )

        # render loop
        while self.running:
            # update time delta
            self.dt = self.clock.tick(self.ctx.cfg.FPS) / 1000.0

            # handle events
            for event in pygame.event.get():
                # match on types
                if event.type == pygame.QUIT:
                    # TODO: need better cleanup logic here
                    self.running = False

                # event handlers
                self.screen_man.process_event(event)

            # update
            self.screen_man.update(self.dt)
            self.ctx.serial_man.update()

            # draw ui
            self.screen_man.draw_ui(self.window_surf)

            # update display
            pygame.display.flip()

        # exit ui
        pygame.quit()
