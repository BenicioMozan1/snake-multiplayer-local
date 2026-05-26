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
- Overlay escurecido com fade revela card de vidro (glass)
- Título neon com glow na cor do vencedor e ranking ordenado
- Confete cai se houver vencedor
- `ENTER` / `START` reinicia; `ESC` volta ao lobby

## Módulos

| Módulo | Responsabilidade |
|---|---|
| `core/config.py` | Constantes de gameplay, cores, grid e tema Twilight |
| `core/sprites.py` | Dataclasses puras (Snake, Food, Particle, FloatingText) |
| `core/systems.py` | Classe `World` — lógica de jogo e pipeline de draw |
| `core/fx.py` | Tema visual: gradiente, grade, vinheta, bokeh e glow |
| `core/utils.py` | Renderização de cobras, maçãs, partículas e textos |
| `core/game.py` | Loop principal, Lobby, Game Over, helpers glass_panel/neon_text |
| `client/hud.py` | HUD glassmorphism com placar, maçã e barra de velocidade |

## Regra de dependência

```
client/ → core/     ✅
core/   → client/   ❌ (proibido, com exceção documentada)
```

**Exceção conhecida:** `core/game.py` importa `client/hud.py`
diretamente, pois `Game` é o orquestrador de topo e precisa
acionar o HUD a cada frame. Todos os outros módulos de `core/`
respeitam a regra.

`core/sprites.py` não importa `pygame` — apenas tipos puros.
`core/systems.py` importa `pygame` apenas para tipos de
fonte e superfície.
