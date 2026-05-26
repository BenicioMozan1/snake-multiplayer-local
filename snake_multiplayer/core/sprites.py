# core/sprites.py
# SNAKE MULTIPLAYER
# Pure data classes — no rendering logic here.

from collections import deque
from dataclasses import dataclass, field

import core.config as C


@dataclass
class Snake:
    """Estado completo de uma cobra."""

    player_id: int
    body: deque[tuple[int, int]]        # índice 0 = cabeça
    direction: tuple[int, int] = field(
        default_factory=lambda: C.RIGHT
    )
    next_dir: tuple[int, int] = field(
        default_factory=lambda: C.RIGHT
    )
    color: tuple = (175, 169, 236)
    color_dark: tuple = (100, 95, 160)
    alive: bool = True
    score: int = 0
    speed: float = C.INITIAL_SPEED
    grow_pending: int = 0
    death_flash: float = 0.0   # timer para piscar vermelho
    death_reason: str = ""

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]


@dataclass
class Food:
    pos: tuple[int, int]
    kind: str = "normal"    # "normal" | "bonus" | "speed"
    value: int = 1
    ttl: float | None = None
    age: float = 0.0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    lifetime: float
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def alpha(self) -> int:
        return max(
            0, int(255 * (1 - self.age / self.lifetime))
        )


@dataclass
class FloatingText:
    """Texto flutuante pós-evento (ex: '+3', 'BONUS!')."""

    text: str
    x: float
    y: float
    color: tuple
    ttl: float = C.FLOATING_TEXT_TTL
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.ttl
