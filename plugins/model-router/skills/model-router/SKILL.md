---
name: model-router
description: Roteia o trabalho por dificuldade para economizar tokens. Use no início de qualquer tarefa de código que envolva explorar o repositório, implementar mudanças ou tomar decisões técnicas. O modelo principal orquestra e delega busca ao scout (Haiku), implementação ao implementer (Sonnet) e decisões difíceis ao architect (Opus).
---

# Model Router

Objetivo: gastar o modelo caro só onde há raciocínio difícil. Você (modelo principal) orquestra; subagentes executam.

## Tabela de roteamento

| Tipo de tarefa | Subagente | Modelo / esforço |
|---|---|---|
| Localizar arquivos, grep, listar estrutura, ler logs, extrair trechos, resumir arquivo grande | `scout` | Haiku / low (somente leitura) |
| Editar conforme plano claro, escrever testes, refatoração mecânica, revisão de código | `implementer` | Sonnet / medium |
| Arquitetura, bug ambíguo ou de causa incerta, trade-offs, plano de mudança grande, revisão final de mudança arriscada | `architect` | Opus / high |

Se os subagentes aparecerem com prefixo de plugin (`model-router:scout`), use o nome completo.

## Regras

1. **Não delegue o que é barato de fazer direto.** Se couber em 1–2 leituras ou uma edição pequena, faça você mesmo. Cada subagente novo carrega system prompt, CLAUDE.md e contexto próprios.
2. **Toda delegação define o formato de retorno.** Ex.: "caminho:linha + 3 linhas de contexto, máximo 30 linhas". Sem isso o ganho de tokens some.
3. **Busca prioriza recall.** Peça ao scout todos os candidatos plausíveis e filtre você. Um trecho omitido não será recuperado, porque você não sabe que existia.
4. **Valide resultado vazio ou suspeito.** Se o scout voltar sem nada, contraditório ou incompleto, refaça UMA vez com outra estratégia (outros termos, outro diretório) antes de concluir. Para afirmações críticas, leia você mesmo o arquivo apontado.
5. **Escale, não rebaixe.** Se um subagente falhar ou pedir escalada, suba um nível. Nunca passe uma tarefa já difícil para um modelo menor no meio do caminho.
6. **Só `implementer` e você escrevem.** O scout é somente leitura; o architect planeja e decide, e a execução mecânica volta para o implementer.
7. **Decisão de design não é delegada para baixo.** Se a escolha tem trade-off real, decida você ou use o architect.
8. **Paralelize o independente.** Várias buscas sem dependência entre si vão em paralelo; o que depende de resultado anterior vai em sequência. Lembre que cada resultado devolvido ocupa seu contexto.
9. **Fluxo típico:** scout mapeia → (architect decide, se houver trade-off) → implementer executa → você revisa o diff e os testes.

## Limites conhecidos

- Subagentes herdam a configuração de extended thinking da sessão; só o `effort` é ajustável por subagente.
- A variável `CLAUDE_CODE_SUBAGENT_MODEL` sobrescreve o modelo dos subagentes; evite defini-la globalmente se quiser este roteamento.
- O roteamento automático depende da descrição de cada subagente. Para forçar, cite o nome ("use o scout para ...") ou use @-menção.
