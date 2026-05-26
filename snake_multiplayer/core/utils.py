# core/utils.py
# SNAKE MULTIPLAYER
# Shared drawing and math helpers (port do Asteroids).

import pygame as pg

import core.config as C

Vec = pg.math.Vector2


def draw_checkerboard(
    surface: pg.Surface,
    light: tuple = None,
    dark: tuple = None,
) -> None:
    """Xadrez de duas cores — estilo Snake clássico."""
    if light is None:
        light = C.COLOR_BG_LIGHT
    if dark is None:
        dark = C.COLOR_BG_DARK
    for col in range(C.COLS):
        for row in range(C.ROWS):
            if (col + row) % 2 == 0:
                color = light
            else:
                color = dark
            rect = pg.Rect(
                col * C.CELL, row * C.CELL,
                C.CELL, C.CELL,
            )
            pg.draw.rect(surface, color, rect)


def draw_border(surface: pg.Surface) -> None:
    """Borda visível da arena (estilo Snake clássico)."""
    pg.draw.rect(
        surface, C.COLOR_BORDER,
        (0, 0, C.WIDTH, C.HEIGHT),
        C.BORDER_WIDTH,
    )


def draw_snake(surface: pg.Surface, snake) -> None:
    cs = C.CELL
    pad = 2

    for i, (col, row) in enumerate(snake.body):
        if not snake.alive:
            # Piscar vermelho ao morrer
            t = snake.death_flash
            if int(t * 10) % 2 == 0:
                color = (180, 30, 30)
            else:
                color = C.COLOR_DEAD
        elif i == 0:
            color = snake.color
        else:
            # Gradiente suave: corpo mais escuro
            body_len = max(len(snake.body) - 1, 1)
            ratio = min(i / body_len, 1.0)
            color = tuple(
                int(
                    snake.color[c] * (1 - ratio * 0.35)
                    + snake.color_dark[c] * ratio * 0.35
                )
                for c in range(3)
            )

        rect = pg.Rect(
            col * cs + pad, row * cs + pad,
            cs - pad * 2, cs - pad * 2,
        )
        pg.draw.rect(surface, color, rect, border_radius=4)

        if i == 0 and snake.alive:
            _draw_eyes(
                surface, col, row, snake.direction, cs
            )


def _draw_eyes(
    surface: pg.Surface,
    col: int, row: int,
    direction: tuple, cs: int,
) -> None:
    cx = col * cs + cs // 2
    cy = row * cs + cs // 2
    dx, dy = direction
    ox, oy = dy * 4, dx * 4   # perpendicular à direção
    fw = 3                     # offset para frente

    for sign in (-1, 1):
        ex = cx + dx * fw + sign * ox
        ey = cy + dy * fw + sign * oy
        pg.draw.circle(
            surface, (255, 255, 255), (ex, ey), 2,
        )
        pg.draw.circle(
            surface, (0, 0, 0), (ex, ey), 1,
        )


def draw_food(surface: pg.Surface, food) -> None:
    cs = C.CELL
    cx = food.pos[0] * cs + cs // 2
    cy = food.pos[1] * cs + cs // 2

    color_map = {
        "normal": C.COLOR_FOOD_NORMAL,
        "bonus": C.COLOR_FOOD_BONUS,
        "speed": C.COLOR_FOOD_SPEED,
    }
    color = color_map.get(food.kind, C.COLOR_FOOD_NORMAL)
    radius = cs // 2 - 3

    # Piscar nos últimos 2s de TTL
    if food.ttl is not None:
        remaining = food.ttl - food.age
        if remaining < 2.0 and int(food.age * 6) % 2 == 0:
            return

    pg.draw.circle(surface, color, (cx, cy), radius)
    pg.draw.circle(
        surface, (255, 255, 255), (cx - 2, cy - 2), 2,
    )


def draw_particles(
    surface: pg.Surface, particles: list,
) -> None:
    for p in particles:
        if p.alpha <= 0:
            continue
        size = max(1, int(3 * (1 - p.age / p.lifetime)))
        pg.draw.circle(
            surface, p.color,
            (int(p.x), int(p.y)), size,
        )


def draw_floating_texts(
    surface: pg.Surface,
    texts: list,
    font: pg.font.Font,
) -> None:
    for t in texts:
        alpha = max(
            0, int(255 * (1 - t.age / t.ttl))
        )
        surf = font.render(t.text, True, t.color)
        surf.set_alpha(alpha)
        surface.blit(
            surf,
            (int(t.x) - surf.get_width() // 2, int(t.y)),
        )
