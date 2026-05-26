# core/fx.py
# SNAKE MULTIPLAYER
# Camadas visuais do tema "Twilight": gradiente, grade, vinheta,
# partículas de ambiente (bokeh) e brilho (glow). As superfícies
# pesadas são geradas uma única vez e reaproveitadas a cada frame.

import math
import random

import pygame as pg

import core.config as C

# ── Caches de superfícies (criadas sob demanda) ───────────────
_gradient: pg.Surface | None = None
_grid: pg.Surface | None = None
_vignette: pg.Surface | None = None
_soft: pg.Surface | None = None
_glow_cache: dict = {}
_bokeh: list[dict] = []


# ─────────────────────────────────────────────────────────────
#  Geração das camadas estáticas
# ─────────────────────────────────────────────────────────────

def _sample_stops(stops: list, t: float) -> tuple:
    """Interpola a cor de um gradiente multi-stop na posição t."""
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            f = (t - p0) / max(p1 - p0, 1e-6)
            return tuple(
                int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3)
            )
    return stops[-1][1]


def _build_gradient() -> pg.Surface:
    """Gradiente vertical do tema (1px de largura, esticado)."""
    h = C.HEIGHT
    strip = pg.Surface((1, h))
    for y in range(h):
        strip.set_at((0, y), _sample_stops(C.BG_GRADIENT, y / (h - 1)))
    return pg.transform.scale(strip, (C.WIDTH, C.HEIGHT))


def _build_grid() -> pg.Surface:
    """Grade luminosa fina alinhada às células."""
    surf = pg.Surface((C.WIDTH, C.HEIGHT), pg.SRCALPHA)
    col = (*C.GRID_COLOR, 255)
    for x in range(0, C.WIDTH + 1, C.CELL):
        pg.draw.line(surf, col, (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT + 1, C.CELL):
        pg.draw.line(surf, col, (0, y), (C.WIDTH, y))
    return surf


def _build_vignette() -> pg.Surface:
    """Vinheta radial (escurece as bordas). Gerada pequena e
    esticada com suavização para sair barata e macia."""
    sw, sh = 96, 72
    small = pg.Surface((sw, sh), pg.SRCALPHA)
    cx, cy = sw / 2, sh / 2
    maxd = math.hypot(cx, cy)
    for x in range(sw):
        for y in range(sh):
            d = math.hypot(x - cx, y - cy) / maxd
            a = int(C.VIGNETTE_STRENGTH * max(0.0, (d - 0.45) / 0.55))
            small.set_at((x, y), (0, 0, 0, min(255, max(0, a))))
    return pg.transform.smoothscale(small, (C.WIDTH, C.HEIGHT))


def _soft_circle() -> pg.Surface:
    """Sprite base de brilho: círculo branco com alpha que cai
    suave do centro para a borda. Usado em todo glow do jogo."""
    global _soft
    if _soft is None:
        d = 128
        _soft = pg.Surface((d, d), pg.SRCALPHA)
        r = d / 2
        for i in range(int(r), 0, -1):
            a = int(235 * (1 - i / r) ** 2)
            pg.draw.circle(_soft, (255, 255, 255, a), (int(r), int(r)), i)
    return _soft


# ─────────────────────────────────────────────────────────────
#  Glow reaproveitável
# ─────────────────────────────────────────────────────────────

def draw_glow(
    surface: pg.Surface,
    pos: tuple,
    radius: float,
    color: tuple,
    alpha: float = 1.0,
) -> None:
    """Desenha um halo macio colorido centrado em pos."""
    radius = max(2, int(radius))
    key = (color, radius)
    spr = _glow_cache.get(key)
    if spr is None:
        spr = pg.transform.smoothscale(
            _soft_circle(), (radius * 2, radius * 2),
        )
        spr = spr.copy()
        spr.fill((*color, 255), special_flags=pg.BLEND_RGBA_MULT)
        if len(_glow_cache) < 600:
            _glow_cache[key] = spr
    spr.set_alpha(int(max(0.0, min(1.0, alpha)) * 255))
    surface.blit(spr, (pos[0] - radius, pos[1] - radius))


# ─────────────────────────────────────────────────────────────
#  Partículas de ambiente (bokeh)
# ─────────────────────────────────────────────────────────────

def _init_bokeh() -> None:
    rng = random.Random(7)
    palette = [C.NEON_CYAN, C.NEON_PINK, C.NEON_VIOLET, (130, 200, 255)]
    for _ in range(18):
        _bokeh.append({
            "x": rng.uniform(0, C.WIDTH),
            "y": rng.uniform(0, C.HEIGHT),
            "r": rng.uniform(18, 64),
            "spd": rng.uniform(5, 16),
            "sway": rng.uniform(10, 30),
            "phase": rng.uniform(0, math.tau),
            "color": rng.choice(palette),
            "alpha": rng.uniform(0.05, 0.14),
        })


def _draw_bokeh(surface: pg.Surface, t: float) -> None:
    if not _bokeh:
        _init_bokeh()
    for b in _bokeh:
        # Sobe devagar (com wrap) e balança no eixo x.
        y = (b["y"] - t * b["spd"]) % (C.HEIGHT + 120) - 60
        x = b["x"] + math.sin(t * 0.5 + b["phase"]) * b["sway"]
        draw_glow(surface, (int(x), int(y)), b["r"], b["color"], b["alpha"])


# ─────────────────────────────────────────────────────────────
#  API pública
# ─────────────────────────────────────────────────────────────

def draw_background(surface: pg.Surface) -> None:
    """Fundo completo: gradiente + grade pulsante + bokeh."""
    global _gradient, _grid
    if _gradient is None:
        _gradient = _build_gradient()
    if _grid is None:
        _grid = _build_grid()

    t = pg.time.get_ticks() / 1000.0
    surface.blit(_gradient, (0, 0))

    # Grade com leve pulso de opacidade.
    pulse = int(C.GRID_ALPHA + 8 * math.sin(t * 1.5))
    _grid.set_alpha(max(0, pulse))
    surface.blit(_grid, (0, 0))

    _draw_bokeh(surface, t)


def draw_vignette(surface: pg.Surface) -> None:
    """Escurece as bordas para focar o olhar no centro."""
    global _vignette
    if _vignette is None:
        _vignette = _build_vignette()
    surface.blit(_vignette, (0, 0))
