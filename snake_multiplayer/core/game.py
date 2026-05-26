# core/game.py
# SNAKE MULTIPLAYER
# Main game loop: Lobby → Play → Game Over.

import math
import random
import sys
from dataclasses import dataclass

import pygame as pg

import core.config as C
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
        from core.utils import draw_checkerboard

        draw_checkerboard(
            surf,
            light=C.LOBBY_BG_LIGHT,
            dark=C.LOBBY_BG_DARK,
        )

        # Título Moderno
        title = self.big.render("SNAKE", True, C.WHITE)
        surf.blit(
            title,
            (C.WIDTH // 2 - title.get_width() // 2, 40),
        )

        mode_name = C.MODES[self.mode_idx]["label"]
        sub = self.medium.render(
            f"◀  {mode_name}  ▶",
            True, C.WHITE,
        )
        sub_bg = pg.Surface((sub.get_width() + 40, sub.get_height() + 20), pg.SRCALPHA)
        pg.draw.rect(sub_bg, (30, 30, 40, 200), sub_bg.get_rect(), border_radius=15)
        surf.blit(sub_bg, (C.WIDTH // 2 - sub_bg.get_width() // 2, 110))
        surf.blit(
            sub,
            (C.WIDTH // 2 - sub.get_width() // 2, 120),
        )

        # Grid moderno horizontal
        card_w = 180
        card_h = 240
        gap = 30
        total_w = (card_w * 4) + (gap * 3)
        start_x = (C.WIDTH - total_w) // 2
        start_y = 220

        for i in range(4):
            pid = i + 1
            x = start_x + i * (card_w + gap)
            y = start_y
            color = self.COLORS[i]
            is_joined = pid in self.bindings

            rect = pg.Rect(x, y, card_w, card_h)
            
            # Fundo do card
            bg_color = (25, 25, 35) if is_joined else (20, 20, 25)
            pg.draw.rect(surf, bg_color, rect, border_radius=15)
            
            # Borda (brilha se joined)
            border_color = color if is_joined else (40, 40, 50)
            pg.draw.rect(
                surf, border_color, rect,
                3 if is_joined else 2,
                border_radius=15,
            )

            # Header do Card (Player Name)
            header_rect = pg.Rect(x, y, card_w, 50)
            pg.draw.rect(surf, border_color, header_rect, border_top_left_radius=15, border_top_right_radius=15)
            
            lbl_color = C.BLACK if is_joined else C.GRAY
            lbl = self.medium.render(
                f"PLAYER {pid}", True, lbl_color,
            )
            surf.blit(lbl, (x + card_w//2 - lbl.get_width()//2, y + 10))

            if is_joined:
                b = self.bindings[pid]
                st = self.small.render(
                    self._input_label(b), True, C.WHITE,
                )
            else:
                st = self.small.render(
                    "Aguardando...", True, C.GRAY,
                )
            surf.blit(
                st,
                (x + card_w//2 - st.get_width()//2, y + 80),
            )

            cy = y + 130
            if is_joined:
                lines = self._control_lines(
                    self.bindings[pid]
                )
            else:
                lines = [
                    "Pressione",
                    "qualquer botão",
                    "para entrar",
                ]
            for line in lines:
                txt_color = color if is_joined else C.GRAY
                s = self.small.render(
                    line, True, txt_color,
                )
                surf.blit(s, (x + card_w//2 - s.get_width()//2, cy))
                cy += 25

        # Instrução de início pulsante
        y_bot = C.HEIGHT - 80
        if self.get_joined_count() >= 2:
            pulse = int(
                180 + 75 * math.sin(self.t * 5)
            )
            start = self.medium.render(
                "PRESSIONE START PARA JOGAR",
                True, (pulse, pulse, pulse),
            )
            surf.blit(
                start,
                (
                    C.WIDTH // 2
                    - start.get_width() // 2,
                    y_bot,
                ),
            )
        else:
            hint = self.font.render(
                "Aguardando mínimo de 2 jogadores",
                True, C.GRAY,
            )
            surf.blit(
                hint,
                (
                    C.WIDTH // 2
                    - hint.get_width() // 2,
                    y_bot,
                ),
            )


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

    def _draw_game_over(self, dt: float) -> None:
        """Tela de game over com overlay sobre o grid."""

        alpha = min(255, int(self.go_fade * 255))
        overlay = pg.Surface(
            (C.WIDTH, C.HEIGHT), pg.SRCALPHA,
        )
        overlay.fill((10, 10, 15, min(210, alpha))) # Fundo mais escuro
        self.screen.blit(overlay, (0, 0))

        winner_id = self.world.winner_id
        scores = self.world.scores

        # Card de Game Over
        card_w, card_h = 560, 480
        card_x = (C.WIDTH - card_w) // 2
        card_y = (C.HEIGHT - card_h) // 2
        
        card_surface = pg.Surface((card_w, card_h), pg.SRCALPHA)
        card_surface.set_alpha(alpha)
        pg.draw.rect(card_surface, (25, 25, 35, 255), (0, 0, card_w, card_h), border_radius=20)
        pg.draw.rect(card_surface, (50, 50, 60, 255), (0, 0, card_w, card_h), width=2, border_radius=20)
        
        self.screen.blit(card_surface, (card_x, card_y))

        # Título
        if winner_id is not None:
            color = C.PLAYER_COLORS[winner_id - 1]
            title_surf = self.big.render(
                "VITÓRIA!", True, color,
            )
            winner_text = f"PLAYER {winner_id} VENCEU"
        else:
            color = C.WHITE
            title_surf = self.big.render(
                "EMPATE", True, C.WHITE,
            )
            winner_text = "TODOS MORRERAM"

        title_surf.set_alpha(alpha)
        self.screen.blit(
            title_surf,
            (
                C.WIDTH // 2 - title_surf.get_width() // 2,
                card_y + 30,
            ),
        )

        w_surf = self.medium.render(
            winner_text, True, C.WHITE,
        )
        w_surf.set_alpha(alpha)
        self.screen.blit(
            w_surf,
            (
                C.WIDTH // 2 - w_surf.get_width() // 2,
                card_y + 90,
            ),
        )

        # Motivo da vitória
        reason_surf = self.font.render(
            self.world.win_reason, True, C.GRAY_LIGHT,
        )
        reason_surf.set_alpha(alpha)
        self.screen.blit(
            reason_surf,
            (
                C.WIDTH // 2 - reason_surf.get_width() // 2,
                card_y + 120,
            ),
        )

        # Resumo de cada jogador
        sorted_snakes = sorted(
            self.world.snakes.values(),
            key=lambda s: s.score,
            reverse=True,
        )
        y = card_y + 170
        for s in sorted_snakes:
            p_id = s.player_id
            p_color = C.PLAYER_COLORS[p_id - 1]
            
            # Barra do jogador
            bar_w = 460
            bar_rect = pg.Rect(C.WIDTH // 2 - bar_w//2, y, bar_w, 40)
            pg.draw.rect(self.screen, (35, 35, 45, alpha), bar_rect, border_radius=10)
            
            s_surf = self.medium.render(
                f"P{p_id}", True, p_color
            )
            s_surf.set_alpha(alpha)
            self.screen.blit(s_surf, (C.WIDTH // 2 - bar_w//2 + 15, y + 5))
            
            # Status ou pontuação
            if not s.alive:
                status_text = s.death_reason
                status_color = C.COLOR_DEAD
            else:
                if winner_id == p_id:
                    status_text = f"Sobrevivente! Score: {s.score:02d}"
                    status_color = C.COLOR_FOOD_BONUS
                else:
                    status_text = f"Score: {s.score:02d}"
                    status_color = C.WHITE

            score_surf = self.font.render(
                status_text, True, status_color
            )
            score_surf.set_alpha(alpha)
            self.screen.blit(score_surf, (C.WIDTH // 2 + bar_w//2 - score_surf.get_width() - 15, y + 8))
            
            y += 50

        # Instrução de reinício (pulsar após fade)
        if self.go_fade >= 0.8:
            pulse = int(
                150 + 105 * math.sin(self.go_fade * 8)
            )
            restart = self.medium.render(
                "START para jogar novamente   |   ESC para voltar",
                True, (pulse, pulse, pulse),
            )
            self.screen.blit(
                restart,
                (
                    C.WIDTH // 2 - restart.get_width() // 2,
                    C.HEIGHT - 80,
                ),
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
