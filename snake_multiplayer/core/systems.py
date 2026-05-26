# core/systems.py
# SNAKE MULTIPLAYER
# Coordinates world state, movement, collisions, scoring,
# and progression.

import math
import random
from collections import deque

import pygame as pg

import core.config as C
from core.sprites import FloatingText, Food, Particle, Snake


class World:
    def __init__(self, font: pg.font.Font, bindings: dict):
        self.font = font
        self.bindings = dict(bindings)

        # ── Dicionários dinâmicos (2-4 jogadores) ─────────
        self.snakes: dict[int, Snake] = {}
        self.scores: dict[int, int] = {}

        # ── Criar cobras para cada binding ────────────────
        for p_id in self.bindings:
            i = p_id - 1
            col, row = C.SNAKE_STARTS[i]
            direction = C.SNAKE_DIRECTIONS[i]

            # Corpo inicial: HEAD + (LENGTH-1) na dir oposta
            opp = C.OPPOSITE[direction]
            body = deque(
                (col + opp[0] * j, row + opp[1] * j)
                for j in range(C.SNAKE_START_LENGTH)
            )
            self.snakes[p_id] = Snake(
                player_id=p_id,
                body=body,
                direction=direction,
                next_dir=direction,
                color=C.PLAYER_COLORS[i],
                color_dark=C.PLAYER_DARK[i],
                speed=C.INITIAL_SPEED,
            )
            self.scores[p_id] = 0

        # ── Comidas e partículas ──────────────────────────
        self.foods: list[Food] = []
        self.particles: list[Particle] = []
        self.texts: list[FloatingText] = []
        self.accumulator: float = 0.0

        # Abastecer comidas iniciais
        while len(self.foods) < C.MAX_FOODS_ON_SCREEN:
            self.foods.append(self._spawn_food())

        # ── Estado da partida ─────────────────────────────
        self.game_over = False
        self.winner_id: int | None = None
        self.win_reason: str = ""

    # ─────────────────────────────────────────────────────
    #  Update principal
    # ─────────────────────────────────────────────────────

    def update(
        self, dt: float, keys, joysticks: dict,
    ) -> None:
        if self.game_over:
            return

        # 1. Input → next_dir de cada cobra
        for p_id, snake in self.snakes.items():
            if not snake.alive:
                continue
            binding = self.bindings[p_id]
            self._handle_snake_input(
                snake, binding, keys, joysticks,
            )

        # 2. Movimento discreto (tick acumulado)
        self.accumulator += dt
        self._move_snakes()

        # 3. Comida: TTL, colisão, respawn
        self._food_system(dt)

        # 4. Colisões (parede, auto, P×P)
        self._collision_system()

        # 5. Partículas e textos flutuantes
        self._particle_system(dt)

        # 6. Condição de fim
        self._check_end()

    # ─────────────────────────────────────────────────────
    #  Draw
    # ─────────────────────────────────────────────────────

    def draw(
        self, surface: pg.Surface, font: pg.font.Font,
    ) -> None:
        """Port de World.draw() do Asteroids."""
        from core.utils import (
            draw_border,
            draw_checkerboard,
            draw_floating_texts,
            draw_food,
            draw_particles,
            draw_snake,
        )

        draw_checkerboard(surface)
        draw_border(surface)

        for food in self.foods:
            draw_food(surface, food)

        draw_particles(surface, self.particles)

        for snake in self.snakes.values():
            draw_snake(surface, snake)

        draw_floating_texts(surface, self.texts, self.font)

    # ─────────────────────────────────────────────────────
    #  Input
    # ─────────────────────────────────────────────────────

    def _handle_snake_input(
        self, snake: Snake, binding, keys,
        joysticks: dict,
    ) -> None:
        """Lê teclas/eixos e seta snake.next_dir."""
        desired = None

        if binding.input_type == C.INPUT_KEYBOARD_WASD:
            if keys[pg.K_w]:
                desired = C.UP
            elif keys[pg.K_s]:
                desired = C.DOWN
            elif keys[pg.K_a]:
                desired = C.LEFT
            elif keys[pg.K_d]:
                desired = C.RIGHT

        elif binding.input_type == C.INPUT_KEYBOARD_ARROWS:
            if keys[pg.K_UP]:
                desired = C.UP
            elif keys[pg.K_DOWN]:
                desired = C.DOWN
            elif keys[pg.K_LEFT]:
                desired = C.LEFT
            elif keys[pg.K_RIGHT]:
                desired = C.RIGHT

        elif binding.input_type == C.INPUT_GAMEPAD:
            joy = joysticks.get(binding.joy_instance_id)
            if joy:
                ax = joy.get_axis(0)
                ay = joy.get_axis(1)
                hat = (
                    joy.get_hat(0)
                    if joy.get_numhats() > 0
                    else (0, 0)
                )
                hx, hy = hat

                if abs(ax) > abs(ay) and ax < -0.4:
                    desired = C.LEFT
                elif abs(ax) > abs(ay) and ax > 0.4:
                    desired = C.RIGHT
                elif abs(ay) > abs(ax) and ay < -0.4:
                    desired = C.UP
                elif abs(ay) > abs(ax) and ay > 0.4:
                    desired = C.DOWN
                # D-pad sobrescreve analógico
                if hx == -1:
                    desired = C.LEFT
                elif hx == 1:
                    desired = C.RIGHT
                elif hy == 1:
                    desired = C.UP
                elif hy == -1:
                    desired = C.DOWN

        # Aplicar: proíbe reversão de 180°
        if desired and desired != C.OPPOSITE.get(
            snake.direction
        ):
            snake.next_dir = desired

    # ─────────────────────────────────────────────────────
    #  Movimento
    # ─────────────────────────────────────────────────────

    def _move_snakes(self) -> None:
        """Avanço discreto por tick acumulado."""
        alive_snakes = [
            s for s in self.snakes.values() if s.alive
        ]
        if not alive_snakes:
            tick = 1.0 / C.INITIAL_SPEED
        else:
            tick = 1.0 / max(s.speed for s in alive_snakes)

        if self.accumulator < tick:
            return
        self.accumulator -= tick

        for snake in self.snakes.values():
            if not snake.alive:
                continue

            snake.direction = snake.next_dir
            dx, dy = snake.direction
            hc, hr = snake.head
            new_head = (hc + dx, hr + dy)

            if C.WRAP_BORDERS:
                new_head = (
                    new_head[0] % C.COLS,
                    new_head[1] % C.ROWS,
                )

            snake.body.appendleft(new_head)
            if snake.grow_pending > 0:
                snake.grow_pending -= 1
            else:
                snake.body.pop()

    # ─────────────────────────────────────────────────────
    #  Comida
    # ─────────────────────────────────────────────────────

    def _food_system(self, dt: float) -> None:
        to_remove: list[Food] = []

        for food in self.foods:
            if food.ttl is not None:
                food.age += dt
                if food.age >= food.ttl:
                    to_remove.append(food)

        for snake in self.snakes.values():
            if not snake.alive:
                continue
            for food in self.foods:
                if food in to_remove:
                    continue
                if snake.head == food.pos:
                    snake.score += food.value
                    self.scores[snake.player_id] += (
                        food.value
                    )
                    snake.grow_pending += food.value
                    if food.kind == "speed":
                        snake.speed = min(
                            snake.speed
                            + C.SPEED_INCREMENT * 3,
                            C.MAX_SPEED,
                        )
                    else:
                        snake.speed = min(
                            snake.speed + C.SPEED_INCREMENT,
                            C.MAX_SPEED,
                        )
                    to_remove.append(food)
                    # Partículas de comer
                    self._spawn_particles(
                        food.pos,
                        C.PARTICLE_COUNT_EAT,
                        snake.color,
                    )
                    # Texto flutuante
                    cx = (
                        food.pos[0] * C.CELL + C.CELL // 2
                    )
                    cy = (
                        food.pos[1] * C.CELL + C.CELL // 2
                    )
                    label = (
                        f"+{food.value}"
                        if food.value == 1
                        else f"+{food.value} BONUS!"
                    )
                    self.texts.append(
                        FloatingText(
                            label, cx, cy, snake.color,
                        )
                    )

        for f in to_remove:
            if f in self.foods:
                self.foods.remove(f)

        while len(self.foods) < C.MAX_FOODS_ON_SCREEN:
            self.foods.append(self._spawn_food())

    def _spawn_food(self) -> Food:
        occupied: set[tuple] = set()
        for s in self.snakes.values():
            occupied.update(s.body)
        for f in self.foods:
            occupied.add(f.pos)

        pos = (
            random.randint(1, C.COLS - 2),
            random.randint(1, C.ROWS - 2),
        )
        for _ in range(200):
            pos = (
                random.randint(1, C.COLS - 2),
                random.randint(1, C.ROWS - 2),
            )
            if pos not in occupied:
                break

        roll = random.random()
        if roll < C.BONUS_FOOD_CHANCE * 0.4:
            return Food(pos, "speed", 1, C.BONUS_FOOD_TTL)
        if roll < C.BONUS_FOOD_CHANCE:
            return Food(pos, "bonus", 3, C.BONUS_FOOD_TTL)
        return Food(pos, "normal", 1, None)

    # ─────────────────────────────────────────────────────
    #  Colisão
    # ─────────────────────────────────────────────────────

    def _collision_system(self) -> None:
        deaths: list[tuple[Snake, str]] = []

        for snake in self.snakes.values():
            if not snake.alive:
                continue

            col, row = snake.head

            # Parede (só se não houver wrap)
            if not C.WRAP_BORDERS:
                if not (0 <= col < C.COLS and 0 <= row < C.ROWS):
                    deaths.append((snake, "bateu de cabeça na parede"))
                    continue

            # Auto-colisão
            if (col, row) in list(snake.body)[1:]:
                deaths.append((snake, "bateu no próprio corpo"))
                continue

            # Colisão com outras cobras
            if C.COLLISION_MODE == "lethal":
                for other in self.snakes.values():
                    if other.player_id == snake.player_id:
                        continue
                    
                    # Checar cabeça com cabeça
                    if snake.head == other.head:
                        deaths.append((snake, "bateu de frente com outra cobra"))
                        break
                    
                    # Checar corpo (ignorando a cabeça do outro, já que checamos acima)
                    if (col, row) in list(other.body)[1:]:
                        deaths.append((snake, f"bateu no P{other.player_id}"))
                        break

        # Aplicar todas as mortes do tick simultaneamente
        for s, reason in deaths:
            if s.alive:
                self._kill_snake(s, reason)

    def _kill_snake(self, snake: Snake, reason: str = "") -> None:
        snake.alive = False
        snake.death_reason = reason
        snake.death_flash = 0.5
        self._spawn_particles(
            snake.head,
            C.PARTICLE_COUNT_DEATH,
            snake.color,
        )

    # ─────────────────────────────────────────────────────
    #  Partículas
    # ─────────────────────────────────────────────────────

    def _spawn_particles(
        self,
        cell: tuple[int, int],
        count: int,
        color: tuple,
    ) -> None:
        cx = cell[0] * C.CELL + C.CELL // 2
        cy = cell[1] * C.CELL + C.CELL // 2
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(40, C.PARTICLE_SPEED)
            lt = random.uniform(
                C.PARTICLE_LIFETIME * 0.5,
                C.PARTICLE_LIFETIME,
            )
            self.particles.append(
                Particle(
                    x=float(cx),
                    y=float(cy),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    color=color,
                    lifetime=lt,
                )
            )

    def _particle_system(self, dt: float) -> None:
        for p in self.particles:
            p.age += dt
            p.x += p.vx * dt
            p.y += p.vy * dt
        self.particles = [
            p for p in self.particles if p.alive
        ]

        for t in self.texts:
            t.age += dt
            t.y -= 30 * dt
        self.texts = [t for t in self.texts if t.alive]

    # ─────────────────────────────────────────────────────
    #  Condição de fim
    # ─────────────────────────────────────────────────────

    def _check_end(self) -> None:
        alive = [
            s for s in self.snakes.values() if s.alive
        ]

        # Modo corrida: alguém atingiu FOOD_TO_WIN
        for snake in self.snakes.values():
            if snake.score >= C.FOOD_TO_WIN:
                self.winner_id = snake.player_id
                self.win_reason = "Atingiu a pontuação máxima!"
                self.game_over = True
                return

        # Sobrevivência / todos mortos
        if not alive:
            # Encontra o maior score e os jogadores empatados
            max_score = max(self.scores.values())
            top_players = [
                pid for pid, score in self.scores.items() if score == max_score
            ]
            
            if len(top_players) > 1:
                self.winner_id = None
                self.win_reason = "Empate! Empatados no score máximo."
            else:
                self.winner_id = top_players[0]
                self.win_reason = "Todos morreram. Vitória por pontos!"
            self.game_over = True
        elif (
            len(alive) == 1 and len(self.snakes) > 1
        ):
            self.winner_id = alive[0].player_id
            self.win_reason = "Foi o único a sobreviver!"
            self.game_over = True
