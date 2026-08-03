# std
from typing import TYPE_CHECKING

# extern
import pygame_gui

# local
import axonkit

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppContext


def create_manager(ctx: AppContext) -> pygame_gui.UIManager:
    man = pygame_gui.UIManager(
        ctx.cfg.WINDOW_SIZE,
        axonkit.DEFAULT_THEME,
    )
    man.get_theme().load_theme(ctx.cfg.THEME_FILE)
    return man
