# client/hud.py
# SNAKE MULTIPLAYER
# Dual/quad scoreboard — shown above the grid during play.

import pygame as pg

import core.config as C


class HUD:
    """
    Placar para 2-4 jogadores.
    Cada slot mostra: nome · score · barra de velocidade.
    Layout horizontal no topo, dividido igualmente.
    """

    FONT_SIZE = 20
    SMALL_SIZE = 14
    BAR_H = 5
    SLOT_H = 38

    def __init__(self) -> None:
        self.font = pg.font.SysFont(
            "consolas", self.FONT_SIZE, bold=True,
        )
        self.small = pg.font.SysFont(
            "consolas", self.SMALL_SIZE,
        )

    def draw(
        self,
        surface: pg.Surface,
        snakes: dict,          # {player_id: Snake}
        food_to_win: int,
    ) -> None:
        n = len(snakes)
        if n == 0:
            return
        sw = C.WIDTH // n
        pad = 10

        for i, (pid, snake) in enumerate(
            sorted(snakes.items())
        ):
            x = i * sw + pad
            y = 4
            if snake.alive:
                color = snake.color
            else:
                color = C.COLOR_DEAD

            # Rótulo P1…P4
            lbl = self.font.render(
                f"P{pid}", True, color,
            )
            surface.blit(lbl, (x, y))

            # Score
            sc = self.font.render(
                f"{snake.score:02d}/{food_to_win}",
                True, C.WHITE,
            )
            surface.blit(
                sc, (x + lbl.get_width() + 8, y),
            )

            # Barra de velocidade
            bar_x = x
            bar_y = y + self.FONT_SIZE + 4
            bar_w = sw - pad * 2
            speed_range = max(
                C.MAX_SPEED - C.INITIAL_SPEED, 1,
            )
            ratio = max(
                0.0,
                min(
                    1.0,
                    (snake.speed - C.INITIAL_SPEED)
                    / speed_range,
                ),
            )
            pg.draw.rect(
                surface, (40, 40, 50),
                (bar_x, bar_y, bar_w, self.BAR_H),
                border_radius=2,
            )
            if ratio > 0:
                pg.draw.rect(
                    surface, color,
                    (
                        bar_x, bar_y,
                        int(bar_w * ratio), self.BAR_H,
                    ),
                    border_radius=2,
                )
