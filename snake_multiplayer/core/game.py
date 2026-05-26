# core/game.py
# SNAKE MULTIPLAYER
# Main game loop: Lobby → Play → Game Over.

import math
import random
import sys
from dataclasses import dataclass

import pygame as pg

import core.config as C
import core.fx as fx
from client.hud import HUD
from core.systems import World


# ── InputBinding ──────────────────────────────────────────
@dataclass
class InputBinding:
    """Descreve como um jogador controla sua cobra."""

    input_type: str           # C.INPUT_KEYBOARD_*
    joy_instance_id: int = -1


@dataclass
class Scene:
    name: str


# ── Helpers visuais compartilhados (lobby + game over) ────
def glass_panel(
    surface: pg.Surface,
    rect: pg.Rect,
    border_color: tuple,
    alpha: int = C.PANEL_ALPHA,
    radius: int = 16,
    glow: float = 0.14,
) -> None:
    """Painel translúcido com brilho no topo e borda luminosa."""
    if glow > 0:
        fx.draw_glow(
            surface, rect.center,
            max(rect.w, rect.h) * 0.55, border_color, glow,
        )
    panel = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(panel, (*C.PANEL_BG, alpha), panel.get_rect(), border_radius=radius)
    pg.draw.rect(
        panel, (255, 255, 255, 26),
        (4, 3, rect.w - 8, rect.h // 2), border_radius=max(2, radius - 2),
    )
    pg.draw.rect(
        panel, (*border_color, 230),
        panel.get_rect(), width=2, border_radius=radius,
    )
    surface.blit(panel, (rect.x, rect.y))


def neon_text(
    surface: pg.Surface,
    font: pg.font.Font,
    text: str,
    center: tuple,
    color: tuple,
    glow_alpha: float = 0.55,
) -> tuple:
    """Texto branco com halo colorido + contorno neon."""
    ts = font.render(text, True, C.WHITE)
    tc = font.render(text, True, color)
    w, h = ts.get_size()
    fx.draw_glow(surface, center, max(w, h) * 0.7, color, glow_alpha)
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        c = tc.copy()
        c.set_alpha(130)
        surface.blit(c, (center[0] - w // 2 + ox, center[1] - h // 2 + oy))
    surface.blit(ts, (center[0] - w // 2, center[1] - h // 2))
    return w, h


class Lobby:
    """
    Lobby moderno de entrada.
    Jogadores entram pressionando WASD, Setas ou
    botão A no controle. Layout horizontal e limpo.
    """

    COLORS = C.PLAYER_COLORS

    WASD_KEYS = {pg.K_w, pg.K_a, pg.K_s, pg.K_d}
    ARROW_KEYS = {
        pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT,
    }

    def __init__(self, font, big, medium):
        self.font = font
        self.big = big
        self.medium = medium
        self.small = pg.font.SysFont("segoe ui", 16) # Modern font
        self.t = 0.0

        self.bindings: dict[int, InputBinding] = {}
        self.keyboard_wasd_taken = False
        self.keyboard_arrows_taken = False
        self.joy_taken: set[int] = set()

        # Modo selecionado (índice em C.MODES)
        self.mode_idx = 0

    def _next_player_id(self) -> int:
        for pid in range(1, C.MAX_TOTAL_PLAYERS + 1):
            if pid not in self.bindings:
                return pid
        return -1

    def try_join_keyboard_wasd(self) -> bool:
        if self.keyboard_wasd_taken:
            return False
        if len(self.bindings) >= C.MAX_TOTAL_PLAYERS:
            return False
        pid = self._next_player_id()
        if pid == -1:
            return False
        self.bindings[pid] = InputBinding(
            C.INPUT_KEYBOARD_WASD,
        )
        self.keyboard_wasd_taken = True
        return True

    def try_join_keyboard_arrows(self) -> bool:
        if self.keyboard_arrows_taken:
            return False
        if len(self.bindings) >= C.MAX_TOTAL_PLAYERS:
            return False
        pid = self._next_player_id()
        if pid == -1:
            return False
        self.bindings[pid] = InputBinding(
            C.INPUT_KEYBOARD_ARROWS,
        )
        self.keyboard_arrows_taken = True
        return True

    def try_join_gamepad(self, instance_id: int) -> bool:
        if instance_id in self.joy_taken:
            return False
        if len(self.bindings) >= C.MAX_TOTAL_PLAYERS:
            return False
        pid = self._next_player_id()
        if pid == -1:
            return False
        self.bindings[pid] = InputBinding(
            C.INPUT_GAMEPAD,
            joy_instance_id=instance_id,
        )
        self.joy_taken.add(instance_id)
        return True

    def get_player_for_joy(
        self, instance_id: int,
    ) -> "int | None":
        for pid, b in self.bindings.items():
            if (
                b.input_type == C.INPUT_GAMEPAD
                and b.joy_instance_id == instance_id
            ):
                return pid
        return None

    def get_joined_count(self) -> int:
        return len(self.bindings)

    def _input_label(self, b: InputBinding) -> str:
        if b.input_type == C.INPUT_KEYBOARD_WASD:
            return "TECLADO (WASD)"
        if b.input_type == C.INPUT_KEYBOARD_ARROWS:
            return "TECLADO (SETAS)"
        return "CONTROLE"

    def _control_lines(
        self, b: InputBinding,
    ) -> list[str]:
        if b.input_type == C.INPUT_KEYBOARD_WASD:
            return ["WASD — mover"]
        if b.input_type == C.INPUT_KEYBOARD_ARROWS:
            return ["Setas — mover"]
        return ["Analógico esq. / D-pad"]

    def update(self, dt: float):
        self.t += dt

    def draw(self, surf: pg.Surface):
        fx.draw_background(surf)

        # ── Título com glow + pequena flutuação ───────────────
        bob = int(math.sin(self.t * 2) * 4)
        neon_text(
            surf, self.big, "SNAKE",
            (C.WIDTH // 2, 70 + bob), C.NEON_VIOLET, glow_alpha=0.6,
        )

        # ── Seletor de modo (pílula de vidro) ─────────────────
        mode = C.MODES[self.mode_idx]
        pill = pg.Rect(0, 0, 360, 46)
        pill.center = (C.WIDTH // 2, 138)
        glass_panel(surf, pill, C.NEON_CYAN, radius=23, glow=0.18)
        neon_text(
            surf, self.medium, f"◀  {mode['label']}  ▶",
            pill.center, C.NEON_CYAN, glow_alpha=0.0,
        )
        desc = self.small.render(mode["desc"], True, C.GRAY_LIGHT)
        surf.blit(desc, (C.WIDTH // 2 - desc.get_width() // 2, 168))

        # ── Cards dos jogadores ───────────────────────────────
        card_w, card_h, gap = 180, 250, 30
        total_w = (card_w * 4) + (gap * 3)
        start_x = (C.WIDTH - total_w) // 2
        start_y = 210

        for i in range(4):
            pid = i + 1
            x = start_x + i * (card_w + gap)
            color = self.COLORS[i]
            is_joined = pid in self.bindings
            rect = pg.Rect(x, start_y, card_w, card_h)

            if is_joined:
                # Pulso luminoso quando o jogador entrou.
                pulse = 0.18 + 0.12 * (0.5 + 0.5 * math.sin(self.t * 4 + i))
                glass_panel(surf, rect, color, glow=pulse)
                border = color
            else:
                glass_panel(surf, rect, (70, 66, 95), alpha=120, glow=0.0)
                border = (90, 86, 120)

            # Avatar: orbe luminoso na cor do jogador.
            orb = (rect.centerx, start_y + 56)
            if is_joined:
                fx.draw_glow(surf, orb, 34, color, 0.6)
            pg.draw.circle(surf, color if is_joined else (80, 78, 105), orb, 16)
            pg.draw.circle(surf, C.WHITE, (orb[0] - 5, orb[1] - 5), 4)

            # Nome do jogador.
            lbl = self.medium.render(f"PLAYER {pid}", True, color if is_joined else C.GRAY)
            surf.blit(lbl, (rect.centerx - lbl.get_width() // 2, start_y + 92))

            # Status do controle.
            if is_joined:
                status = self._input_label(self.bindings[pid])
                st = self.small.render(status, True, C.WHITE)
            else:
                st = self.small.render("Aguardando...", True, C.GRAY)
            surf.blit(st, (rect.centerx - st.get_width() // 2, start_y + 130))

            # Linhas de ajuda / controles.
            if is_joined:
                lines = self._control_lines(self.bindings[pid])
            else:
                lines = ["Pressione", "qualquer botão", "para entrar"]
            cy = start_y + 165
            for line in lines:
                s = self.small.render(line, True, color if is_joined else C.GRAY)
                surf.blit(s, (rect.centerx - s.get_width() // 2, cy))
                cy += 24

        # ── Chamada para iniciar (pulsante) ───────────────────
        y_bot = C.HEIGHT - 70
        if self.get_joined_count() >= 2:
            glow = 0.4 + 0.3 * (0.5 + 0.5 * math.sin(self.t * 5))
            neon_text(
                surf, self.medium, "PRESSIONE START PARA JOGAR",
                (C.WIDTH // 2, y_bot), C.NEON_PINK, glow_alpha=glow,
            )
        else:
            hint = self.font.render(
                "Aguardando mínimo de 2 jogadores", True, C.GRAY_LIGHT,
            )
            surf.blit(hint, (C.WIDTH // 2 - hint.get_width() // 2, y_bot - 8))


class Game:
    """Loop principal — Lobby → Play → Game Over."""

    def __init__(self):
        pg.init()
        pg.joystick.init()

        self.screen = pg.display.set_mode(
            (C.WIDTH, C.HEIGHT),
        )
        pg.display.set_caption("Snake Multiplayer")
        self.clock = pg.time.Clock()

        # Fontes modernas
        self.font = pg.font.SysFont("segoe ui", 18)
        self.big = pg.font.SysFont(
            "segoe ui", 56, bold=True,
        )
        self.medium = pg.font.SysFont(
            "segoe ui", 24, bold=True,
        )

        # Joysticks ativos
        self.joysticks: dict[int, pg.Joystick] = {}

        # Subsistemas
        self.hud = HUD()

        # Cena inicial
        self.scene = Scene("lobby")
        self.lobby = Lobby(
            self.font, self.big, self.medium,
        )

        # Game Over state
        self.world: World | None = None
        self.go_fade = 0.0
        self.confetti: list[dict] = []

    def _start_game(self):
        """Aplica modo selecionado e inicia partida."""
        mode = C.MODES[self.lobby.mode_idx]
        C.WRAP_BORDERS = mode["wrap"]
        C.COLLISION_MODE = mode["collision"]
        self.world = World(
            self.font, self.lobby.bindings,
        )
        self.scene = Scene("play")

    def _reset_lobby(self):
        """Volta ao lobby resetando tudo."""
        self.lobby = Lobby(
            self.font, self.big, self.medium,
        )
        self.scene = Scene("lobby")
        self.world = None
        self.go_fade = 0.0
        self.confetti = []

    def _spawn_confetti(self, base_color: tuple) -> None:
        """Cria papéis picados caindo do topo (só na vitória)."""
        import random
        palette = [base_color, C.NEON_CYAN, C.NEON_PINK, C.NEON_VIOLET, C.WHITE]
        self.confetti = [{
            "x": random.uniform(0, C.WIDTH),
            "y": random.uniform(-C.HEIGHT, 0),
            "vy": random.uniform(80, 180),
            "sway": random.uniform(20, 60),
            "phase": random.uniform(0, 6.28),
            "size": random.randint(4, 8),
            "color": random.choice(palette),
        } for _ in range(90)]

    def _draw_confetti(self, dt: float) -> None:
        """Atualiza e desenha o confete."""
        t = pg.time.get_ticks() / 1000.0
        for c in self.confetti:
            c["y"] += c["vy"] * dt
            x = int(c["x"] + math.sin(t * 2 + c["phase"]) * c["sway"])
            y = int(c["y"])
            pg.draw.rect(
                self.screen, c["color"],
                (x, y, c["size"], c["size"] + 2), border_radius=2,
            )
        # Remove o que saiu pela base.
        self.confetti = [c for c in self.confetti if c["y"] < C.HEIGHT + 20]

    def _draw_game_over(self, dt: float) -> None:
        """Tela de vitória: overlay escurecido, confete, card de
        vidro com glow, título neon e ranking dos jogadores."""

        alpha = min(255, int(self.go_fade * 255))

        # Escurece o jogo ao fundo.
        overlay = pg.Surface((C.WIDTH, C.HEIGHT), pg.SRCALPHA)
        overlay.fill((8, 6, 18, min(220, alpha)))
        self.screen.blit(overlay, (0, 0))

        # Confete (só quando há vencedor).
        if self.confetti:
            self._draw_confetti(dt)

        winner_id = self.world.winner_id

        # Card de vidro central.
        card_w, card_h = 580, 500
        card = pg.Rect(0, 0, card_w, card_h)
        card.center = (C.WIDTH // 2, C.HEIGHT // 2)

        if winner_id is not None:
            accent = C.PLAYER_COLORS[winner_id - 1]
            title = "VITÓRIA!"
            subtitle = f"PLAYER {winner_id} VENCEU"
        else:
            accent = C.NEON_CYAN
            title = "EMPATE"
            subtitle = "TODOS MORRERAM"

        glass_panel(self.screen, card, accent, radius=22, glow=0.22)

        # Título e subtítulo neon.
        neon_text(self.screen, self.big, title, (card.centerx, card.y + 56), accent)
        sub = self.medium.render(subtitle, True, C.WHITE)
        self.screen.blit(sub, (card.centerx - sub.get_width() // 2, card.y + 96))

        reason = self.font.render(self.world.win_reason, True, C.GRAY_LIGHT)
        self.screen.blit(reason, (card.centerx - reason.get_width() // 2, card.y + 128))

        # Ranking dos jogadores (ordenado por score).
        sorted_snakes = sorted(
            self.world.snakes.values(), key=lambda s: s.score, reverse=True,
        )
        row_w = card_w - 60
        y = card.y + 168
        for s in sorted_snakes:
            p_color = C.PLAYER_COLORS[s.player_id - 1]
            row = pg.Rect(card.centerx - row_w // 2, y, row_w, 44)
            is_winner = winner_id == s.player_id
            glass_panel(
                self.screen, row, p_color if is_winner else (80, 76, 110),
                alpha=140, radius=12, glow=0.16 if is_winner else 0.0,
            )

            tag = self.medium.render(f"P{s.player_id}", True, p_color)
            self.screen.blit(tag, (row.x + 16, row.y + 9))

            if not s.alive:
                status, scolor = s.death_reason, C.COLOR_DEAD
            elif is_winner:
                status, scolor = f"Campeão!  {s.score:02d} pts", C.COLOR_FOOD_BONUS
            else:
                status, scolor = f"{s.score:02d} pts", C.WHITE
            ssurf = self.font.render(status, True, scolor)
            self.screen.blit(ssurf, (row.right - ssurf.get_width() - 16, row.y + 13))
            y += 52

        # Instrução de reinício (pulsa após o fade).
        if self.go_fade >= 0.8:
            glow = 0.4 + 0.3 * (0.5 + 0.5 * math.sin(self.go_fade * 6))
            neon_text(
                self.screen, self.font,
                "START para jogar novamente    |    ESC para o lobby",
                (C.WIDTH // 2, C.HEIGHT - 50), C.NEON_PINK, glow_alpha=glow,
            )

    def run(self):
        """Loop principal — idêntico ao Asteroids."""
        running = True
        while running:
            dt = self.clock.tick(C.FPS) / 1000.0
            keys = pg.key.get_pressed()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False

                # ── Joystick hotplug ──────────────
                elif e.type == pg.JOYDEVICEADDED:
                    joy = pg.Joystick(e.device_index)
                    joy.init()
                    self.joysticks[
                        joy.get_instance_id()
                    ] = joy

                elif e.type == pg.JOYDEVICEREMOVED:
                    self.joysticks.pop(
                        e.instance_id, None,
                    )

                # ── Lobby events ──────────────────
                elif (
                    e.type == pg.KEYDOWN
                    and self.scene.name == "lobby"
                ):
                    # Join WASD
                    if e.key in Lobby.WASD_KEYS:
                        self.lobby.try_join_keyboard_wasd()

                    # Join Setas
                    elif e.key in Lobby.ARROW_KEYS:
                        self.lobby.try_join_keyboard_arrows()

                    # Trocar modo
                    elif e.key == pg.K_LEFT:
                        self.lobby.mode_idx = (
                            self.lobby.mode_idx - 1
                        ) % len(C.MODES)
                    elif e.key == pg.K_RIGHT:
                        self.lobby.mode_idx = (
                            self.lobby.mode_idx + 1
                        ) % len(C.MODES)

                    # Iniciar partida
                    elif e.key in (
                        pg.K_RETURN, pg.K_KP_ENTER,
                    ):
                        if (
                            self.lobby.get_joined_count()
                            >= 2
                        ):
                            self._start_game()

                elif (
                    e.type == pg.JOYBUTTONDOWN
                    and self.scene.name == "lobby"
                ):
                    iid = e.instance_id
                    # Botão A (0) = join
                    if e.button == 0:
                        self.lobby.try_join_gamepad(iid)
                    # Start (7 ou 6) = iniciar
                    elif e.button in (6, 7):
                        if (
                            self.lobby.get_joined_count()
                            >= 2
                        ):
                            self._start_game()

                # ── Play events ───────────────────
                elif (
                    e.type == pg.KEYDOWN
                    and self.scene.name == "play"
                ):
                    if e.key == pg.K_ESCAPE:
                        self._reset_lobby()

                # ── Game Over events ──────────────
                elif (
                    e.type == pg.KEYDOWN
                    and self.scene.name == "game_over"
                ):
                    if self.go_fade >= 0.8:
                        if e.key in (
                            pg.K_RETURN,
                            pg.K_KP_ENTER,
                        ):
                            # Reiniciar partida
                            self._start_game()
                        elif e.key == pg.K_ESCAPE:
                            self._reset_lobby()

                elif (
                    e.type == pg.JOYBUTTONDOWN
                    and self.scene.name == "game_over"
                ):
                    if self.go_fade >= 0.8:
                        if e.button in (6, 7):
                            self._start_game()

            # ── Scene update & draw ───────────────
            self.screen.fill(C.COLOR_BG)

            if self.scene.name == "lobby":
                self.lobby.update(dt)
                self.lobby.draw(self.screen)

            elif self.scene.name == "play":
                self.world.update(
                    dt, keys, self.joysticks,
                )
                self.world.draw(
                    self.screen, self.font,
                )
                self.hud.draw(
                    self.screen,
                    self.world.snakes,
                    C.FOOD_TO_WIN,
                )
                if self.world.game_over:
                    self.go_fade = 0.0
                    self.scene = Scene("game_over")
                    if self.world.winner_id is not None:
                        self._spawn_confetti(
                            C.PLAYER_COLORS[self.world.winner_id - 1],
                        )

            elif self.scene.name == "game_over":
                self.go_fade += dt / (
                    C.GAME_OVER_FADE_DURATION
                )
                # Redraw world underneath
                if self.world:
                    self.world.draw(
                        self.screen, self.font,
                    )
                    self.hud.draw(
                        self.screen,
                        self.world.snakes,
                        C.FOOD_TO_WIN,
                    )
                self._draw_game_over(dt)

            pg.display.flip()

        pg.quit()
        sys.exit()
