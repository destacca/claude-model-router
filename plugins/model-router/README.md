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
- Para tarefas pequenas, delegar custa mais que fazer direto; a skill instrui a não delegar nesses casos.
- Não defina `CLAUDE_CODE_SUBAGENT_MODEL` globalmente, ou ele sobrescreve o modelo de cada agente.

## Testes e resultados

Data: 06/11/2026. Alvo: repositório público `expressjs/express` (commit 43fca52). Tarefas de exploração com gabarito calculado por `grep`:

- **T1:** listar toda linha de `lib/*.js` com a palavra `locals` (gabarito: 10 linhas).
- **T2:** listar os arquivos de `test/` que mencionam `sendFile` (gabarito: 2 arquivos).

Mesmo prompt, subagente `general-purpose` com o modelo trocado. Tokens = total reportado por subagente.

| Tarefa | Modelo | Tokens | Tempo | Resultado |
|---|---|---|---|---|
| T1 | Haiku (4 execuções) | 64.3k a 64.9k | 4,4 a 7,8 s | 3 corretas, 1 com 9/10 (perdeu `application.js:172`, um comentário) |
| T1 | Sonnet | 63,7k | 5,1 s | 10/10 |
| T1 | Opus | 63,8k | 4,8 s | 10/10 |
| T2 | Haiku | 64,2k | 4,6 s | 2/2 |
| T2 | Sonnet | 63,6k | 6,0 s | 2/2 |
| T2 | Opus | 63,7k | 6,0 s | 2/2 |

### O que os testes mostram

1. **Contagem de tokens não muda com o modelo.** Todas as execuções ficaram em ~64k tokens, dominadas pelo custo fixo de iniciar um subagente (system prompt e definições de ferramentas). A economia vem do preço por token do modelo menor, que **não foi medido aqui**.
2. **Delegar tarefa trivial sai mais caro.** Um único `grep` direto resolve T1 e T2 com uma fração desses ~64k tokens. Por isso a regra 1 da skill (não delegar o que é barato) vale mais que qualquer troca de modelo.
3. **O Haiku errou 1 de 5 execuções em T1/T2**, omitindo uma ocorrência dentro de comentário, sem avisar. Confirma o risco de recall: o orquestrador não percebe o que não foi retornado.
4. **Qualidade nas demais execuções foi igual entre modelos** nessas tarefas de busca literal.

### Limites desta medição

- Amostra pequena (10 execuções, 2 tarefas, 1 repositório). Não é estatisticamente conclusivo.
- Subagente `general-purpose` com todas as ferramentas. O `scout` do plugin (só `Read`, `Grep`, `Glob`) deve ter menos overhead, mas **não foi medido**.
- **Não foi testado o ciclo completo** (orquestrador escolhendo sozinho quando delegar) nem tarefas de implementação com Sonnet/Opus. Não consegui rodar `claude -p` no ambiente de teste (sem autenticação).
- Custo em dólares não foi calculado.

Se você medir com o plugin em uso real, contribuições com resultados são bem-vindas.

## Licença

MIT
