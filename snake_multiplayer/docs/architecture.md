# Arquitetura — Snake Multiplayer Local

## Visão Geral

O projeto segue a mesma arquitetura do `asteroids_multiplayer`:
separação clara entre **core** (lógica pura) e **client**
(renderização, HUD).

## Fluxo de Cenas

```
Lobby ──▶ Play ──▶ Game Over
  ▲                    │
  └────────────────────┘
```

### Lobby (`scene.name == "lobby"`)
- Até 4 jogadores entram pressionando WASD, Setas ou
  botão A no controle
- Mínimo de 2 jogadores para iniciar
- `←` / `→` troca o modo de jogo
- `ENTER` / `START` inicia a partida

### Play (`scene.name == "play"`)
- `World.update(dt, keys, joysticks)` processa toda a
  lógica: input, movimento, colisão, comida, partículas
- `World.draw(surface, font)` renderiza o estado
- `HUD.draw()` exibe placar e barra de velocidade
- `ESC` volta ao lobby

### Game Over (`scene.name == "game_over"`)
- Overlay com fade mostra vencedor e placar ordenado
- `ENTER` / `START` reinicia; `ESC` volta ao lobby

## Módulos

| Módulo | Responsabilidade |
|---|---|
| `core/config.py` | Constantes de gameplay, cores, grid |
| `core/sprites.py` | Dataclasses puras (Snake, Food, etc.) |
| `core/systems.py` | Classe `World` — lógica de jogo |
| `core/utils.py` | Helpers de desenho (grid, cobra, comida) |
| `core/game.py` | Loop principal, Lobby, Scene, InputBinding |
| `client/hud.py` | HUD com placar e barra de velocidade |

## Regra de dependência

```
client/ → core/     ✅
core/   → client/   ❌ (proibido)
```

`core/sprites.py` não importa `pygame` — apenas tipos puros.
`core/systems.py` importa `pygame` apenas para tipos de
fonte e superfície.
