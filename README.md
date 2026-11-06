# model-router

Plugin do Claude Code que reduz o gasto de tokens roteando o trabalho por dificuldade:

- **scout** (Haiku, low, somente leitura): busca, grep, leitura e extração de trechos.
- **implementer** (Sonnet, medium): implementação de mudanças já especificadas, testes, revisão.
- **architect** (Opus, high): arquitetura, bugs ambíguos, trade-offs.

A skill `model-router` ensina o modelo principal a orquestrar esses subagentes e define as regras de delegação.

## Instalação

```
claude plugin marketplace add destacca/claude-model-router
claude plugin install model-router@model-router
```

Ou, dentro de uma sessão: `/plugin marketplace add destacca/claude-model-router`.

## Uso

Depois de instalado, a skill é carregada automaticamente em tarefas de código. Para forçar: `/model-router:model-router` ou peça "use o scout para ...".

## Avisos

- Funciona somente no Claude Code (CLI, desktop, web). Não roda no claude.ai chat nem na API pura.
- O Haiku pode omitir trechos relevantes. A skill mitiga com busca ampla e revalidação, mas não elimina o risco.
- Delegar 1–2 buscas não compensa; a partir de ~4 chamadas sim. O maior ganho isolado é usar Sonnet como modelo principal (ver Testes e resultados).
- Não defina `CLAUDE_CODE_SUBAGENT_MODEL` globalmente, ou ele sobrescreve o modelo de cada agente.

## Testes e resultados

Data: 06/11/2026. Alvo: repositório público `expressjs/express` (commit 43fca52). Gabarito calculado por `grep`. Subagentes `general-purpose` com o modelo trocado. "Tokens" é o valor reportado por subagente (tamanho do contexto atingido, não o total faturado, ver nota abaixo). Scripts em `benchmarks/`.

### Rodada 1: modelos diferentes, mesma tarefa de busca

| Tarefa | Modelo | Tokens | Resultado |
|---|---|---|---|
| T1: linhas de `lib/*.js` com `locals` (10) | Haiku (4 execuções) | 64,3k a 64,9k | 3 corretas, 1 com 9/10 (perdeu um comentário) |
| T1 | Sonnet / Opus | 63,7k / 63,8k | 10/10 |
| T2: arquivos de `test/` com `sendFile` (2) | Haiku / Sonnet / Opus | 64,2k / 63,6k / 63,7k | 2/2 em todos |

### Rodada 2: hipóteses sobre onde o custo está

| Hipótese | Teste | Resultado |
|---|---|---|
| H1: existe um piso fixo por subagente | Haiku sem ferramentas ("responda ok") | **62,6k tokens com 0 chamadas.** Confirmada |
| H2: o custo cresce com o nº de chamadas | Buscar 8 definições em `response.js`, 4 execuções | 64,4k a 64,9k com 2–3 chamadas; ~+1k por chamada. **Refutada**: o piso domina |
| H3: pedir "uma única chamada de Grep" reduz o custo | Mesma tarefa com essa instrução | Os agentes ainda fizeram 2–3 chamadas; sem efeito. **Refutada** |
| H4: Explore tem menos overhead que general-purpose | 2 execuções com Explore (Haiku) | Corretas (2/2), mas o tamanho não foi reportado. **Não medida** |

Todas as execuções de H2/H3 acertaram 8/8.

Nota: com 3 chamadas de API por subagente, o valor reportado (~64k) é menor do que a soma das leituras de contexto, então ele representa o tamanho do contexto e não o total faturado. O custo real é maior que o número sugere e depende de cache.

### Modelo de custo (preços oficiais, `benchmarks/costmodel.py`)

Preços por MTok: Opus 5.5 entrada 4 / cache escrita 5 / cache leitura 0,20 / saída 20; Sonnet 5.5: 2 / 2,5 / 0,10 / 10; Haiku 5.5: 0,10 / 0,125 / 0,01 / 0,50. Premissas: piso de 62,6k tokens por subagente, +1k por chamada, 20 turnos restantes na sessão.

Economia de delegar a exploração ao Haiku, comparada a fazer direto no principal (cache do subagente frio):

| Principal | Contexto | 1 busca | 4 chamadas | 10 chamadas |
|---|---|---|---|---|
| Opus | 20k | -9% | 40% | 77% |
| Opus | 100k | -2% | 21% | 53% |
| Sonnet | 20k | -19% | 34% | 73% |
| Sonnet | 100k | -4% | 19% | 52% |

Tarefa de implementação de 10 chamadas (saída de 5k tokens):

| Contexto | Opus direto | Opus + subagente Sonnet | Tudo no Sonnet |
|---|---|---|---|
| 20k | US$0,58 | US$0,40 | US$0,29 |
| 100k | US$1,06 | US$0,74 | US$0,53 |

### Conclusões

1. **Correção da rodada anterior:** a afirmação de que "delegar tarefa trivial sai mais caro" estava incompleta. Em tokens, sim; em dólares, uma única busca fica praticamente empatada (de -19% a +0%), porque os tokens do Haiku são muito mais baratos. O que perde dinheiro é delegar 1–2 buscas, não um custo enorme.
2. **Delegar exploração ao Haiku compensa a partir de ~4 chamadas** e mais quanto maior o contexto principal.
3. **O maior ganho isolado não é subagente:** rodar o principal em Sonnet em vez de Opus cortou cerca de 50% da tarefa de implementação no modelo, sem nenhum overhead. Orquestrar com Opus e delegar ao Sonnet economiza menos que simplesmente usar Sonnet como principal.
4. **Cada spawn de Sonnet/Opus a frio custa ~US$0,16/US$0,31 só de piso.** Agrupe o trabalho numa única delegação.
5. **O Haiku perdeu uma ocorrência em 1 de 5 execuções de busca**, sem avisar.

### Limites desta medição

- Os dólares são **estimativas de um modelo**, não faturamento medido. Dependem de cache, que não consegui observar.
- Amostra pequena, 1 repositório, tarefas de busca literal. A qualidade em implementação e raciocínio não foi comparada entre modelos.
- O piso de 62,6k foi medido num ambiente com muitas ferramentas e servidores MCP. Num setup enxuto será menor. Restringir `tools` e `omitClaudeMd` em um subagente deve reduzir o piso, mas não foi testado.
- Não foi testado o ciclo completo (orquestrador decidindo sozinho quando delegar). Não consegui rodar `claude -p` no ambiente de teste (sem autenticação).

## Licença

MIT
