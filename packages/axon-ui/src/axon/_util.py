# extern
import pygame

type RectLike = pygame.Rect | tuple[int, int, int, int]


def as_rect(rectlike: RectLike) -> pygame.Rect:
    """
    Convert a `RectLike` to a `pygame.Rect`.
    """
    return (
        rectlike
        if isinstance(rectlike, pygame.Rect)
        else pygame.Rect(rectlike[0], rectlike[1], rectlike[2], rectlike[3])
    )
