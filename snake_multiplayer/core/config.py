# SNAKE MULTIPLAYER
# Stores all gameplay, rendering, and balancing constants.

# ── Tela ──────────────────────────────────────────────────────
WIDTH = 960
HEIGHT = 720
FPS = 60

# ── Grid ──────────────────────────────────────────────────────
CELL = 20                      # pixels por célula
COLS = WIDTH // CELL           # 48 colunas
ROWS = HEIGHT // CELL          # 36 linhas

# ── Velocidade ────────────────────────────────────────────────
INITIAL_SPEED = 8.0            # células/segundo
MAX_SPEED = 20.0
SPEED_INCREMENT = 0.4          # +0.4/célula comida

# ── Regras de jogo ────────────────────────────────────────────
FOOD_TO_WIN = 40              # modo corrida
MAX_FOODS_ON_SCREEN = 3
BONUS_FOOD_CHANCE = 0.15
BONUS_FOOD_TTL = 8.0
WRAP_BORDERS = False
COLLISION_MODE = "lethal"      # "lethal" | "passthrough"

# ── Tamanho inicial das cobras ────────────────────────────────
SNAKE_START_LENGTH = 4

# ── Direções ──────────────────────────────────────────────────
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# ── Cores dos jogadores (fofas, vibrantes e bem distintas) ────
# Cada cobra tem uma cor clara (corpo) e uma escura (gradiente
# e contorno) para destacar do fundo e não "sumir".
SNAKE_P1_COLOR = (160, 140, 255)   # Uva neon
SNAKE_P2_COLOR = (60, 240, 185)    # Esmeralda neon
SNAKE_P3_COLOR = (255, 120, 165)   # Coral neon
SNAKE_P4_COLOR = (255, 195, 80)    # Tangerina neon

SNAKE_P1_DARK = (92, 70, 190)
SNAKE_P2_DARK = (18, 130, 90)
SNAKE_P3_DARK = (200, 60, 95)
SNAKE_P4_DARK = (205, 120, 25)

PLAYER_COLORS = [
    SNAKE_P1_COLOR, SNAKE_P2_COLOR,
    SNAKE_P3_COLOR, SNAKE_P4_COLOR,
]
PLAYER_DARK = [
    SNAKE_P1_DARK, SNAKE_P2_DARK,
    SNAKE_P3_DARK, SNAKE_P4_DARK,
]

# ── Cores gerais ──────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (240, 240, 252)
GRAY = (150, 150, 175)
GRAY_LIGHT = (185, 185, 210)
COLOR_BG = (16, 14, 32)
COLOR_DEAD = (255, 95, 110)    # Vermelho luminoso para leitura

# ── Tema "Twilight": fundo cósmico em gradiente ───────────────
# Pontos do gradiente vertical (posição 0..1, cor).
BG_GRADIENT = [
    (0.0, (22, 18, 46)),    # topo: índigo profundo
    (0.55, (38, 24, 60)),   # meio: violeta
    (1.0, (58, 30, 70)),    # base: ameixa
]
GRID_COLOR = (140, 125, 220)   # grade luminosa
GRID_ALPHA = 26
VIGNETTE_STRENGTH = 165        # escurecimento das bordas

# ── Cores neon de destaque (UI) ───────────────────────────────
NEON_CYAN = (120, 230, 255)
NEON_PINK = (255, 120, 200)
NEON_VIOLET = (170, 140, 255)

# ── Painéis de vidro (glassmorphism) ──────────────────────────
PANEL_BG = (26, 22, 48)        # base translúcida (alpha aplicado no draw)
PANEL_ALPHA = 165
PANEL_BORDER = (140, 125, 225)

# ── Borda da arena ────────────────────────────────────────────
COLOR_BORDER = (150, 130, 235)
BORDER_WIDTH = 3

# ── Comidas (maçãs): cor principal + cor escura p/ profundidade
COLOR_FOOD_NORMAL = (230, 60, 72)   # maçã vermelha
COLOR_FOOD_BONUS = (255, 196, 54)   # maçã dourada (bônus)
COLOR_FOOD_SPEED = (74, 184, 240)   # maçã azul (velocidade)

COLOR_FOOD_NORMAL_DARK = (180, 35, 50)
COLOR_FOOD_BONUS_DARK = (210, 150, 20)
COLOR_FOOD_SPEED_DARK = (40, 130, 200)

# ── Spawn — 4 cantos ─────────────────────────────────────────
SNAKE1_START = (COLS // 6, ROWS // 2)
SNAKE2_START = (COLS - COLS // 6, ROWS // 2)
SNAKE3_START = (COLS // 6, ROWS // 4)
SNAKE4_START = (COLS - COLS // 6, ROWS // 4)

SNAKE_STARTS = [
    SNAKE1_START, SNAKE2_START,
    SNAKE3_START, SNAKE4_START,
]

SNAKE_DIRECTIONS = [RIGHT, LEFT, RIGHT, LEFT]

# ── Partículas ────────────────────────────────────────────────
PARTICLE_COUNT_EAT = 8
PARTICLE_COUNT_DEATH = 20
PARTICLE_LIFETIME = 0.6
PARTICLE_SPEED = 130.0

# ── Input ─────────────────────────────────────────────────────
MAX_KEYBOARD_PLAYERS = 2
MAX_GAMEPAD_PLAYERS = 4
MAX_TOTAL_PLAYERS = 4

INPUT_KEYBOARD_WASD = "keyboard_wasd"
INPUT_KEYBOARD_ARROWS = "keyboard_arrows"
INPUT_GAMEPAD = "gamepad"

# ── Modos de jogo ─────────────────────────────────────────────
MODES = [
    {
        "id": "race",
        "label": "Corrida",
        "desc": f"Primeiro a {FOOD_TO_WIN} comidas",
        "wrap": False,
        "collision": "lethal",
    },
    {
        "id": "survival",
        "label": "Sobrevivência",
        "desc": "Último vivo vence",
        "wrap": False,
        "collision": "lethal",
    },
    {
        "id": "coop",
        "label": "Cooperativo",
        "desc": "Score conjunto vs tempo",
        "wrap": False,
        "collision": "passthrough",
    },
    {
        "id": "warp",
        "label": "Sem Limites",
        "desc": "Bordas conectam",
        "wrap": True,
        "collision": "lethal",
    },
]

WIN_SCORE = FOOD_TO_WIN

# ── Game Over ─────────────────────────────────────────────────
GAME_OVER_FADE_DURATION = 1.5
FLOATING_TEXT_TTL = 1.4
