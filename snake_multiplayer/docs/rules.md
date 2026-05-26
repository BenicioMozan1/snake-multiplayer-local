# Regras do Jogo — Snake Multiplayer Local

## Modos de Jogo

### Corrida (Race)
- Primeiro jogador a comer **12 comidas** vence
- Bordas são letais
- Colisão entre cobras é letal

### Sobrevivência (Survival)
- Último jogador vivo vence
- Se todos morrerem, maior score vence
- Bordas e colisões são letais

### Cooperativo (Coop)
- Score conjunto da equipe
- Colisão entre cobras é desativada (passthrough)
- Bordas continuam letais

### Sem Limites (Warp)
- Bordas conectam (wrap-around)
- Primeiro a 12 comidas vence
- Colisão entre cobras é letal

## Tipos de Comida

| Tipo | Cor | Valor | TTL | Efeito |
|---|---|---|---|---|
| Normal | Vermelho | +1 | ∞ | Cresce 1 célula |
| Bonus | Dourado | +3 | 8s | Cresce 3 células |
| Speed | Azul | +1 | 8s | +3× incremento de velocidade |

## Mecânicas

- **Reversão 180° bloqueada**: não é possível inverter
  a direção da cobra instantaneamente
- **Velocidade individual**: cada cobra acelera conforme
  come, até o máximo de 20 células/segundo
- **Empate head-to-head**: se duas cabeças ocupam a mesma
  célula no mesmo tick, ambas morrem
- **Auto-colisão**: cobra morre ao colidir com próprio corpo
