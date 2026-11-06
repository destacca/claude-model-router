---
name: model-router
description: Reduz custo de tokens em tarefas de código. Use no início de qualquer tarefa que envolva explorar o repositório, implementar mudanças ou tomar decisões técnicas. Define quando delegar exploração ao scout (Haiku), quando escalar decisões difíceis ao architect (Opus) e quando NÃO delegar.
---

# Model Router

Objetivo: gastar o modelo caro só onde há raciocínio difícil, sem pagar overhead de delegação à toa. Os números abaixo vêm de medições e de um modelo de custo com preços oficiais (ver README do repositório).

## Configuração recomendada

- **Modelo principal: Sonnet.** É o maior ganho isolado: o Sonnet custa metade do Opus em entrada, cache e saída, e não paga piso de subagente.
- **Opus só por escalada:** o principal chama o `architect` para decisões difíceis.
- **Haiku só para exploração volumosa:** via `scout`.

## Tabela de roteamento

| Tipo de tarefa | Quem faz |
|---|---|
| 1–3 buscas ou leituras pequenas | Você mesmo, direto. Não delegue. |
| Exploração com ≥4 chamadas de ferramenta esperadas, ou saída volumosa (>~3k tokens) | `scout` (Haiku, somente leitura) |
| Edição, testes, refatoração | Você mesmo. `implementer` só em tarefa longa (≥10 passos) e numa única delegação |
| Arquitetura, bug ambíguo, trade-off, revisão final de risco | `architect` (Opus) |

Se os subagentes aparecerem com prefixo de plugin (`model-router:scout`), use o nome completo.

## Regras

1. **Cada subagente tem um piso fixo (~62k tokens medidos).** Cada chamada de ferramenta adicional custa só ~1k. Portanto: poucos subagentes, tarefas grandes. Agrupe várias perguntas numa única delegação em vez de várias pequenas.
2. **Delegar exploração compensa quando a conta fecha.** No modelo de custo, o scout empata em 1 busca e economiza ~20% a ~78% com 4 a 10 chamadas, mais quanto maior for o seu contexto. Com 1–2 buscas, faça direto.
3. **Não use Sonnet/Opus como subagente por rotina.** O piso inicial (cache frio) custa ~US$0,16 no Sonnet e ~US$0,31 no Opus só para começar. Se o principal já é Sonnet, delegar implementação ao Sonnet não ganha nada.
4. **Toda delegação define o formato de retorno.** Ex.: "caminho:linha + 3 linhas de contexto, máximo 30 linhas". Sem isso o ganho some.
5. **Busca prioriza recall.** Peça todos os candidatos plausíveis e filtre você. Em teste, o Haiku omitiu uma ocorrência em comentário (1 de 5 execuções); peça para incluir comentários e strings.
6. **Valide resultado vazio ou suspeito.** Se o scout voltar sem nada ou incompleto, refaça UMA vez com outra estratégia. Para afirmações críticas, leia você mesmo o arquivo apontado.
7. **Escale, não rebaixe.** Se um subagente falhar ou pedir escalada, suba um nível.
8. **Decisão de design não é delegada para baixo.** Se a escolha tem trade-off real, decida você ou use o `architect`.
9. **Paralelize o independente;** o dependente vai em sequência.
10. **Mantenha o contexto principal pequeno.** Cada turno relê todo o contexto. Evite despejar arquivos inteiros; prefira trechos. Use `/compact` ou `/clear` entre tarefas não relacionadas.

## Limites conhecidos

- O piso de ~62k tokens foi medido num ambiente com muitas ferramentas e servidores MCP. Num setup enxuto tende a ser menor; confira com `/context`.
- Restringir `tools` e usar `omitClaudeMd` no subagente deveria reduzir o piso, mas isso **não foi medido**.
- Pedir no prompt para "usar uma única chamada" não reduziu as chamadas do Haiku nos testes.
- Subagentes herdam a configuração de extended thinking; só o `effort` é ajustável por subagente.
- `CLAUDE_CODE_SUBAGENT_MODEL` sobrescreve o modelo dos subagentes; evite defini-la globalmente.
