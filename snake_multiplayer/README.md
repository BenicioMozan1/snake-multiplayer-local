# 🐍 Snake Multiplayer Local

Jogo da cobrinha multiplayer local para **2 a 4 jogadores**,
feito em Python com Pygame-CE.

## 🎮 Controles

| Jogador | Dispositivo | Ação |
|---|---|---|
| P1 | Teclado WASD | `W` `A` `S` `D` para mover |
| P2 | Teclado Setas | `↑` `←` `↓` `→` para mover |
| P3-P4 | Controle (Gamepad) | Analógico esq. ou D-pad |

### Lobby
- Pressione qualquer tecla de movimento ou **botão A** no
  controle para entrar
- `←` `→` para trocar o modo de jogo
- `ENTER` ou **START** para iniciar (mín. 2 jogadores)

### Durante o jogo
- `ESC` para voltar ao lobby

### Game Over
- `ENTER` ou **START** para jogar novamente
- `ESC` para voltar ao lobby

## 🏆 Modos de Jogo

- **Corrida** — Primeiro a 12 comidas vence
- **Sobrevivência** — Último vivo vence
- **Cooperativo** — Score conjunto, sem colisão entre cobras
- **Sem Limites** — Bordas conectam (wrap-around)

## 📦 Instalação

```bash
# Clonar o repositório
git clone <repo-url>
cd snake_multiplayer

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

### Requisitos
- Python 3.13+
- pygame-ce >= 2.5.0

## 📁 Estrutura do Projeto

```
snake_multiplayer/
├── client/              # HUD
│   └── hud.py
├── core/                # Lógica de jogo
│   ├── config.py        # Constantes
│   ├── game.py          # Loop principal
│   ├── sprites.py       # Dataclasses
│   ├── systems.py       # World (lógica)
│   └── utils.py         # Helpers de desenho
├── docs/                # Documentação
├── main.py              # Ponto de entrada
├── pyproject.toml
└── requirements.txt
```

## 📜 Licença

Apache 2.0
