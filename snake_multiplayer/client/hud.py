# client/hud.py
# SNAKE MULTIPLAYER
# Dual/quad scoreboard — shown above the grid during play.

import pygame as pg

import core.config as C
import core.fx as fx


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
        from core.utils import _draw_apple

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

            # Painel de vidro: base translúcida + brilho no topo
            # + borda luminosa na cor do jogador.
            pw, ph = sw - pad, self.SLOT_H + 6
            panel = pg.Surface((pw, ph), pg.SRCALPHA)
            pg.draw.rect(
                panel, (*C.PANEL_BG, C.PANEL_ALPHA),
                panel.get_rect(), border_radius=12,
            )
            # Faixa de luz no topo (efeito de vidro).
            pg.draw.rect(
                panel, (255, 255, 255, 28),
                (4, 3, pw - 8, ph // 2 - 2), border_radius=10,
            )
            pg.draw.rect(
                panel, (*color, 230),
                panel.get_rect(), width=2, border_radius=12,
            )
            # Glow externo suave do painel.
            fx.draw_glow(surface, (x + pw // 2, y + ph // 2), pw * 0.55, color, 0.12)
            surface.blit(panel, (x, y))

            # Rótulo P1…P4
            lbl = self.font.render(
                f"P{pid}", True, color,
            )
            surface.blit(lbl, (x + 8, y + 4))

            # Mini maçã indicando os pontos.
            apple_x = x + 8 + lbl.get_width() + 12
            apple_y = y + 4 + self.FONT_SIZE // 2
            _draw_apple(
                surface, apple_x, apple_y, 7,
                C.COLOR_FOOD_NORMAL, C.COLOR_FOOD_NORMAL_DARK,
            )

            # Score
            sc = self.font.render(
                f"{snake.score:02d}/{food_to_win}",
                True, C.WHITE,
            )
            surface.blit(
                sc, (apple_x + 12, y + 4),
            )

            # Barra de velocidade (alinhada ao painel)
            bar_x = x + 8
            bar_y = y + self.FONT_SIZE + 6
            bar_w = sw - pad - 16
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
            # Trilho escuro + preenchimento luminoso.
            pg.draw.rect(
                surface, (50, 46, 70),
                (bar_x, bar_y, bar_w, self.BAR_H),
                border_radius=3,
            )
            if ratio > 0:
                fill_w = int(bar_w * ratio)
                pg.draw.rect(
                    surface, color,
                    (bar_x, bar_y, fill_w, self.BAR_H),
                    border_radius=3,
                )
                fx.draw_glow(
                    surface, (bar_x + fill_w, bar_y + self.BAR_H // 2),
                    10, color, 0.5,
                )
