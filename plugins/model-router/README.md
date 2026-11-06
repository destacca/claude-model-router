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

## Licença

MIT
