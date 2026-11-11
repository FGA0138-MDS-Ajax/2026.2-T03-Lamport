# Métricas e qualidade

Registro do acompanhamento de qualidade feito pelo QA (issue #10), com as métricas M1 a M5 do GQM (Visão, seção 5, Quadro 23) de cada sprint, o status dos casos do roteiro de testes (Quadro 26) e os defeitos encontrados.

**Última atualização:** 10/11/2026, `main` no commit `faac2cf`. A Sprint 4 termina em 11/11; seus valores são parciais.

## Painel das sprints

| Métrica | Esperado | Sprint 2 | Sprint 3 | Sprint 4 (parcial) |
| :-- | :--: | :--: | :--: | :--: |
| **M1.** Cobertura das tabelas de regras por testes | 100% | n/a | 0% | **81,25%** (13/16)* |
| **M2.** Aprovação dos testes automatizados | 100% na `main` | 100% (35/35) | 100% (35/35) | 100% (188/188) |
| **M3.** Testes de segurança aprovados | 100% | n/a | n/a | **40%** (2/5) |
| **M4.** Conclusão da sprint | ≥ 80% | **100%** (3/3) | **29%** (2/7) | **78,6%** (11/14) ou **64,3%** (9/14) pelos critérios |
| **M5.** Defeitos abertos | 0 críticos | 0 | 0 | 0 abertos; 5 propostos (1 alto, 4 médios) |

\* Com os testes da branch `test/regras-selecao-rs1-rs3-rs4`, ainda sem merge; na `main` são 62,5% (10/16).

M1 e M3 de Sprints 2 e 3 não se aplicam porque o módulo de regras e o roteiro de testes só passam a existir na Sprint 4.

## Leitura rápida

- **Nenhum defeito crítico.** Todos os testes automatizados passam na CI; os problemas encontrados são de cobertura e de funcionalidade ainda ausente, não de comportamento errado.
- **TI-03 não é atendido:** o check-in não gera nem grava recomendações ([DEF-01](defeitos.md#def-01)). É a pendência mais importante para a revisão da Sprint 4.
- **Regras de seleção (R-S) sem cobertura aderente ao Quadro 20**, por falta de testes e por divergências que o PO precisa decidir ([matriz](matriz-regras-testes.md)).
- **Critério 3 da seção 2.6** (duas sprints seguidas abaixo de 80%): a Sprint 3 (29%) está abaixo e a Sprint 4 também fica abaixo se não chegar a 80% (hoje 78,6% pelas issues). Vale o PO acompanhar na revisão.

## Páginas

| Página | Conteúdo |
| :-- | :-- |
| [Metodologia](metodologia.md) | Definição de cada métrica, fontes, status dos casos e limitações da coleta. |
| [Sprint 2](sprint-2.md) | Métricas e itens da Sprint 2 (registro retroativo). |
| [Sprint 3](sprint-3.md) | Métricas e itens da Sprint 3 (registro retroativo). |
| [Sprint 4](sprint-4.md) | Métricas, status dos 15 casos do roteiro, conclusão e CI da Sprint 4. |
| [Matriz regra × teste](matriz-regras-testes.md) | M1: cada linha de R-D, R-A e R-S e o teste que a cobre. |
| [Conferência dos PRs](conferencia-prs-sprint-4.md) | Issues #5, #6, #17, #18, #19 e #22: casos existentes, rodando na CI e lacunas. |
| [Defeitos](defeitos.md) | DEF-01 a DEF-05, com severidade e comandos para abrir as issues. |
| [Quadro 26 da Sprint 4](quadro-26-sprint-4.md) | Atualização proposta do roteiro de testes da Visão, para a revisão da sprint. |
| [dados/metricas.csv](dados/metricas.csv) | Todos os valores em formato tabular. |

## Como manter

1. Ao fim de cada sprint, repetir a coleta conforme a [metodologia](metodologia.md) e criar a página `sprint-N.md`.
2. Atualizar a matriz regra × teste sempre que `backend/app/rules/` ou os testes de regras mudarem.
3. Registrar cada defeito como issue `bug` com severidade e atualizar [Defeitos](defeitos.md) com o número da issue.
4. Na revisão da sprint, aplicar o Quadro 26 atualizado em nova versão da Visão (PR na branch `docs`).
