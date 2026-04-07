# module imports
import pygame
import pygame_gui
import time

# item imports
from dataclasses import dataclass
from pathlib import Path
from pygame import Surface
from pygame_gui.elements import UITextEntryLine, UIDropDownMenu

# local item imports
from app_config import AppConfig
from app_state import AppState
from app_types import KeyMapAction


@dataclass(kw_only=True)
class App:
    """
    All logic pertaining to running of the application.
    """

    cfg: AppConfig
    """
    Static application configuration.
    """

    state: AppState
    """
    Mutable application state.
    """

    display_surf: Surface
    """
    The root display surface.
    """

    @staticmethod
    def new(
        testing: bool,
        data_dir: Path,
        camera_index: int | None,
    ) -> App:
        # init pygame
        pygame.init()

        # init config
        cfg = AppConfig.new(
            testing=testing,
            data_dir=data_dir,
            camera_index=camera_index,
        )

        # init state
        state = AppState.new(cfg)

        # pygame config
        pygame.display.set_caption(cfg.APP_NAME)

        # window's surface
        display_surf = pygame.display.set_mode((cfg.WINDOW_W, cfg.WINDOW_H))

        return App(
            display_surf=display_surf,
            cfg=cfg,
            state=state,
        )

    def run(self) -> None:
        # aliases
        cfg = self.cfg
        state = self.state
        display_surf = self.display_surf

        while state.running:
            # update time delta
            state.time_delta = state.clock.tick(cfg.FPS) / 1000.0

            # hangle events
            for event in pygame.event.get():
                # match on types
                if event.type == pygame.QUIT:
                    state.running = False

                elif event.type == pygame.KEYDOWN:
                    # get associated action
                    action = cfg.KEYMAP.get(event.key)

                    # actions
                    if action is KeyMapAction.QUIT:
                        state.running = False

                    # speed actions
                    elif action is KeyMapAction.INC_SPEED:
                        state.speed_increment()
                    elif action is KeyMapAction.DEC_SPEED:
                        state.speed_decrement()

                    # fire actions
                    elif action is KeyMapAction.FIRE and state.data_needed:
                        state.serial_man.fire(state.fire_duration)
                        state.fire(time.time(), state.fire_duration)
                        data_buttons_enable()
                    elif action is KeyMapAction.DESTROY:
                        # TODO: reimplement
                        ...
                    elif action is KeyMapAction.SKIP_DATA:
                        state.unrecorded_fire = None
                        data_buttons_disable()
                    elif action is KeyMapAction.GRID:
                        state.serial_man.grid(state.grid_size)

                    # step movement
                    elif action is KeyMapAction.STEP_LEFT:
                        state.serial_man.step_left(state.speed, state.move_duration)
                    elif action is KeyMapAction.STEP_RIGHT:
                        state.serial_man.step_right(state.speed, state.move_duration)
                    elif action is KeyMapAction.STEP_UP:
                        state.serial_man.step_up(state.speed, state.move_duration)
                    elif action is KeyMapAction.STEP_DOWN:
                        state.serial_man.step_down(state.speed, state.move_duration)

                    # continuous movement
                    elif action is KeyMapAction.MOVE_LEFT:
                        state.serial_man.move_left(state.speed, state.move_duration)
                    elif action is KeyMapAction.MOVE_RIGHT:
                        state.serial_man.move_right(state.speed, state.move_duration)
                    elif action is KeyMapAction.MOVE_UP:
                        state.serial_man.move_up(state.speed, state.move_duration)
                    elif action is KeyMapAction.MOVE_DOWN:
                        state.serial_man.move_down(state.speed, state.move_duration)

                elif event.type == pygame.KEYUP:
                    # get associated action
                    action = cfg.KEYMAP.get(event.key)

                    if action in {
                        KeyMapAction.MOVE_UP,
                        KeyMapAction.MOVE_DOWN,
                        KeyMapAction.MOVE_LEFT,
                        KeyMapAction.MOVE_RIGHT,
                    }:
                        state.serial_man.stop()

                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    event_ui_element: UITextEntryLine = event.ui_element
                    event_text: str = event.text
                    match event_ui_element:
                        case e if e is data_id_input:
                            data_id_input_handle_finish(state, event_text)
                        case e if e is data_strain_input:
                            data_strain_input_handle_finish(state, event_text)
                        case e if e is fire_duration_input:
                            fire_duration_input_handle_finish(state, event_text)
                        case e if e is grid_size_input:
                            grid_size_input_handle_finish(state, event_text)
                        case e if e is move_duration_input:
                            move_duration_input_handle_finish(state, event_text)
                        case e if e is temp_window_input:
                            temp_window_input_handle_finish(state, event_text)

                # dropdown changed
                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    event_ui_element: UIDropDownMenu = event.ui_element
                    event_text: str = event.text
                    match event_ui_element:
                        case e if e is filter_dropdown:
                            filter_dropdown_handle_change(event_text)
                        case e if e is color_dropdown:
                            color_dropdown_handle_change(ddmc_text)

                # let manager process event
                state.ui_man.process_events(event)

            # update managers
            state.serial_man.update()
            state.video_man.update(video_frame, cfg.MARKER_POS)
            countdown_label_update()
            status_box_update(state)
            data_status_box_update(state)
            flash_panel_update(state)
            state.ui_man.update(state.time_delta)

            # draw ui
            display_surf.fill(pygame.Color(120, 120, 120))
            state.ui_man.draw_ui(display_surf)

            # update display
            pygame.display.flip()

        # exit ui
        pygame.quit()
