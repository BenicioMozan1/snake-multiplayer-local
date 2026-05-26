# core/utils.py
# SNAKE MULTIPLAYER
# Helpers de desenho do tema "Twilight": cobras, maçãs,
# partículas e textos — todos com brilho (glow).

import math

import pygame as pg

import core.config as C
import core.fx as fx

Vec = pg.math.Vector2


# ─────────────────────────────────────────────────────────────
#  Helpers de cor
# ─────────────────────────────────────────────────────────────

def _lighten(color: tuple, amt: float) -> tuple:
    """Clareia uma cor em direção ao branco (amt 0..1)."""
    return tuple(min(255, int(c + (255 - c) * amt)) for c in color)


def _scale(color: tuple, factor: float) -> tuple:
    """Escurece/clareia multiplicando os canais."""
    return tuple(max(0, min(255, int(c * factor))) for c in color)


# ─────────────────────────────────────────────────────────────
#  Borda da arena
# ─────────────────────────────────────────────────────────────

_border_glow: pg.Surface | None = None


def draw_border(surface: pg.Surface) -> None:
    """Moldura neon arredondada com leve pulso luminoso.
    O halo é gerado uma vez e reaproveitado (só o alpha pulsa)."""
    global _border_glow
    rect = pg.Rect(2, 2, C.WIDTH - 4, C.HEIGHT - 4)
    if _border_glow is None:
        _border_glow = pg.Surface((C.WIDTH, C.HEIGHT), pg.SRCALPHA)
        pg.draw.rect(
            _border_glow, (*C.COLOR_BORDER, 255),
            rect, width=6, border_radius=18,
        )

    t = pg.time.get_ticks() / 1000.0
    pulse = 0.5 + 0.5 * math.sin(t * 1.5)
    _border_glow.set_alpha(int(60 + 40 * pulse))
    surface.blit(_border_glow, (0, 0))
    pg.draw.rect(
        surface, _lighten(C.COLOR_BORDER, 0.2 * pulse),
        rect, width=C.BORDER_WIDTH, border_radius=18,
    )


# ─────────────────────────────────────────────────────────────
#  Cobra
# ─────────────────────────────────────────────────────────────

def _snake_centers(body: list, cs: int) -> list:
    """Centro em pixels de cada célula do corpo."""
    return [(c * cs + cs // 2, r * cs + cs // 2) for (c, r) in body]


def draw_snake_glow(surface: pg.Surface, snake) -> None:
    """Aura luminosa por baixo do corpo da cobra."""
    cs = C.CELL
    body = list(snake.body)
    if not body:
        return
    color = snake.color if snake.alive else C.COLOR_DEAD
    base_a = 0.16 if snake.alive else 0.10
    centers = _snake_centers(body, cs)
    for i, ctr in enumerate(centers):
        # Cabeça brilha mais que a cauda.
        if i == 0:
            fx.draw_glow(surface, ctr, cs * 1.4, color, base_a + 0.14)
        else:
            fx.draw_glow(surface, ctr, cs * 0.95, color, base_a)


def draw_snake(surface: pg.Surface, snake) -> None:
    """Cobra como tubo contínuo: círculos nos centros + linhas
    grossas conectando-os, contorno escuro e gradiente."""
    cs = C.CELL
    body = list(snake.body)
    if not body:
        return

    n = len(body)
    centers = _snake_centers(body, cs)

    # Cor de cada nó (cabeça clara → cauda escura) ou flash de
    # morte piscando em vermelho.
    if not snake.alive:
        flash = int(snake.death_flash * 10) % 2 == 0
        base = (200, 50, 60) if flash else C.COLOR_DEAD
        node_colors = [base] * n
        outline = _scale(base, 0.4)
    else:
        node_colors = []
        for i in range(n):
            ratio = i / max(n - 1, 1)
            node_colors.append(tuple(
                int(
                    snake.color[k] * (1 - ratio * 0.4)
                    + snake.color_dark[k] * ratio * 0.4
                )
                for k in range(3)
            ))
        outline = _scale(snake.color_dark, 0.55)

    body_w = cs + 2          # transborda um pouco p/ virar 1 peça

    # Pula conexões que "saltam" a tela no modo wrap.
    def adjacent(a: int, b: int) -> bool:
        return (
            abs(body[a][0] - body[b][0])
            + abs(body[a][1] - body[b][1]) == 1
        )

    # Raio de cada nó, com leve afinamento na cauda.
    def radius(i: int, extra: int = 0) -> int:
        r = body_w // 2 + extra
        if n > 4:
            if i == n - 1:
                r -= 3
            elif i == n - 2:
                r -= 1
        return max(2, r)

    # ── Contorno (mais grosso, escuro) ────────────────────────
    for i in range(n - 1):
        if adjacent(i, i + 1):
            w = 2 * min(radius(i, 2), radius(i + 1, 2))
            pg.draw.line(surface, outline, centers[i], centers[i + 1], w)
    for i in range(n):
        pg.draw.circle(surface, outline, centers[i], radius(i, 2))

    # ── Corpo (cauda → cabeça p/ cabeça ficar por cima) ───────
    for i in range(n - 1, -1, -1):
        if i < n - 1 and adjacent(i, i + 1):
            w = 2 * min(radius(i), radius(i + 1))
            pg.draw.line(surface, node_colors[i], centers[i], centers[i + 1], w)
        pg.draw.circle(surface, node_colors[i], centers[i], radius(i))

    # ── Faixa de brilho (glossy) no terço dianteiro ───────────
    if snake.alive:
        sheen = _lighten(snake.color, 0.45)
        third = max(1, n // 3)
        for i in range(third):
            cx, cy = centers[i]
            pg.draw.circle(surface, sheen, (cx - 2, cy - 3), max(1, radius(i) // 3))

    # ── Cabeça: brilho + carinha fofa ─────────────────────────
    if snake.alive:
        hx, hy = centers[0]
        pg.draw.circle(
            surface, _lighten(snake.color, 0.5),
            (hx - 3, hy - 3), max(2, cs // 6),
        )
        _draw_face(surface, body[0][0], body[0][1], snake.direction, cs)


def _draw_face(
    surface: pg.Surface,
    col: int, row: int,
    direction: tuple, cs: int,
) -> None:
    """Olhos grandes fofos + bochechas rosadas na cabeça."""
    cx = col * cs + cs // 2
    cy = row * cs + cs // 2
    dx, dy = direction
    px, py = -dy, dx              # vetor perpendicular à direção

    fwd = cs * 0.14               # quão à frente ficam os olhos
    sep = cs * 0.26               # separação entre os olhos
    eye_r = max(3, cs // 5)
    pupil_r = max(1, eye_r // 2)

    # Bochechas (círculos rosa translúcidos) atrás dos olhos.
    cheek = pg.Surface((cs * 2, cs * 2), pg.SRCALPHA)
    for sign in (-1, 1):
        bx = int(cs + px * (sep + 2) * sign - dx * 2)
        by = int(cs + py * (sep + 2) * sign - dy * 2)
        pg.draw.circle(cheek, (255, 150, 175, 120), (bx, by), max(2, cs // 7))
    surface.blit(cheek, (cx - cs, cy - cs))

    # Olhos brancos com pupila apontando p/ frente + glint.
    for sign in (-1, 1):
        ex = int(cx + dx * fwd + px * sep * sign)
        ey = int(cy + dy * fwd + py * sep * sign)
        pg.draw.circle(surface, (255, 255, 255), (ex, ey), eye_r)
        px_, py_ = int(ex + dx * 1.6), int(ey + dy * 1.6)
        pg.draw.circle(surface, (45, 45, 60), (px_, py_), pupil_r)
        pg.draw.circle(
            surface, (255, 255, 255),
            (ex - 1, ey - 1), max(1, pupil_r // 2),
        )


# ─────────────────────────────────────────────────────────────
#  Comida (maçã)
# ─────────────────────────────────────────────────────────────

def draw_food(surface: pg.Surface, food) -> None:
    """Maçã com aura luminosa e flutuação suave (bob)."""
    cs = C.CELL
    cx = food.pos[0] * cs + cs // 2
    cy = food.pos[1] * cs + cs // 2

    # Piscar nos últimos 2s de TTL (comida temporária).
    if food.ttl is not None:
        remaining = food.ttl - food.age
        if remaining < 2.0 and int(food.age * 6) % 2 == 0:
            return

    # Cor principal + cor escura (profundidade) por tipo.
    palette = {
        "normal": (C.COLOR_FOOD_NORMAL, C.COLOR_FOOD_NORMAL_DARK),
        "bonus": (C.COLOR_FOOD_BONUS, C.COLOR_FOOD_BONUS_DARK),
        "speed": (C.COLOR_FOOD_SPEED, C.COLOR_FOOD_SPEED_DARK),
    }
    main, dark = palette.get(food.kind, palette["normal"])

    # Flutuação e pulso de brilho desencontrados por posição.
    t = pg.time.get_ticks() / 1000.0
    phase = food.pos[0] * 0.7 + food.pos[1] * 0.5
    bob = int(math.sin(t * 3 + phase) * 1.8)
    pulse = 0.5 + 0.5 * math.sin(t * 4 + phase)

    fx.draw_glow(surface, (cx, cy + bob), cs * 1.15, main, 0.35 + 0.2 * pulse)
    _draw_apple(surface, cx, cy + bob, cs // 2 - 2, main, dark)


def _draw_apple(
    surface: pg.Surface,
    cx: int, cy: int, r: int,
    main: tuple, dark: tuple,
) -> None:
    """Maçã = 3 lóbulos arredondados + cabinho + folha + brilho."""
    lobe = max(3, int(r * 0.66))
    off = max(1, int(r * 0.34))
    cyb = cy + int(r * 0.12)
    lobes = [
        (cx - off, cyb),
        (cx + off, cyb),
        (cx, cyb + int(r * 0.18)),
    ]

    # Contorno escuro: mesmos lóbulos um pouco maiores.
    for lx, ly in lobes:
        pg.draw.circle(surface, dark, (int(lx), int(ly)), lobe + 1)
    for lx, ly in lobes:
        pg.draw.circle(surface, main, (int(lx), int(ly)), lobe)

    # Cabinho marrom subindo do topo.
    sx, sy = cx, cyb - lobe
    pg.draw.line(
        surface, (120, 82, 50),
        (sx, sy), (sx + max(1, int(r * 0.12)), int(sy - r * 0.5)),
        max(2, r // 6),
    )

    # Folhinha verde ao lado do cabinho.
    leaf_r = max(2, int(r * 0.32))
    lx = sx + int(r * 0.42)
    ly = int(sy - r * 0.30)
    pg.draw.circle(surface, (120, 210, 120), (lx, ly), leaf_r)
    pg.draw.circle(surface, (88, 178, 96), (lx, ly), leaf_r, 1)

    # Brilho branco no lóbulo esquerdo.
    pg.draw.circle(
        surface, (255, 255, 255),
        (int(cx - off), int(cyb - lobe * 0.4)), max(1, lobe // 3),
    )


# ─────────────────────────────────────────────────────────────
#  Partículas e textos
# ─────────────────────────────────────────────────────────────

def draw_particles(surface: pg.Surface, particles: list) -> None:
    """Faíscas com halo luminoso + núcleo branco."""
    for p in particles:
        if p.alpha <= 0:
            continue
        life = 1 - p.age / p.lifetime
        fx.draw_glow(surface, (int(p.x), int(p.y)), 5 + 7 * life, p.color, life * 0.7)
        size = max(1, int(3 * life))
        pg.draw.circle(
            surface, _lighten(p.color, 0.6),
            (int(p.x), int(p.y)), size,
        )


def draw_floating_texts(
    surface: pg.Surface,
    texts: list,
    font: pg.font.Font,
) -> None:
    """Texto flutuante com sombra e leve 'pop' de escala."""
    for t in texts:
        progress = t.age / t.ttl
        alpha = max(0, int(255 * (1 - progress)))
        # Pop: cresce rápido nos primeiros instantes.
        scale = min(1.0, t.age / 0.12) * 1.1
        if scale <= 0:
            continue

        base = font.render(t.text, True, t.color)
        shadow = font.render(t.text, True, (10, 8, 20))
        if scale != 1.0:
            w = max(1, int(base.get_width() * scale))
            h = max(1, int(base.get_height() * scale))
            base = pg.transform.smoothscale(base, (w, h))
            shadow = pg.transform.smoothscale(shadow, (w, h))
        base.set_alpha(alpha)
        shadow.set_alpha(int(alpha * 0.6))

        x = int(t.x) - base.get_width() // 2
        y = int(t.y)
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(base, (x, y))
