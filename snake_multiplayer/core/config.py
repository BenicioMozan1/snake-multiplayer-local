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
FOOD_TO_WIN = 12               # modo corrida
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

# ── Cores dos jogadores (modernas e vibrantes) ────────────────
SNAKE_P1_COLOR = (130, 120, 255)   # Violeta vibrante
SNAKE_P2_COLOR = (60, 220, 160)    # Menta
SNAKE_P3_COLOR = (255, 120, 140)   # Coral
SNAKE_P4_COLOR = (255, 210, 80)    # Âmbar

SNAKE_P1_DARK = (80, 70, 180)
SNAKE_P2_DARK = (30, 150, 100)
SNAKE_P3_DARK = (180, 70, 85)
SNAKE_P4_DARK = (180, 140, 40)

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
WHITE = (235, 235, 245)
GRAY = (100, 105, 120)
GRAY_LIGHT = (140, 145, 160)
COLOR_BG = (18, 18, 24)
COLOR_DEAD = (80, 35, 40)

# ── Background moderno (elegante light green) ─────────────────
COLOR_BG_LIGHT = (160, 205, 135)  # gramado claro
COLOR_BG_DARK = (145, 190, 120)   # gramado escuro
COLOR_BORDER = (80, 110, 60)      # borda da arena
BORDER_WIDTH = 4                  # pixels

# ── Lobby ─────────────────────────────────────────────────────
LOBBY_BG_LIGHT = (140, 185, 115)
LOBBY_BG_DARK = (130, 175, 105)

# ── Comidas ───────────────────────────────────────────────────
COLOR_FOOD_NORMAL = (255, 75, 85)
COLOR_FOOD_BONUS = (255, 200, 50)
COLOR_FOOD_SPEED = (60, 190, 255)

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
