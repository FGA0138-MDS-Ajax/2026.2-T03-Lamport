# Métricas e qualidade

Registro do acompanhamento de qualidade feito pelo QA (issue #10), com as métricas M1 a M5 do GQM (Visão, seção 5, Quadro 23) de cada sprint, o status dos casos do roteiro de testes (Quadro 26) e os defeitos encontrados.

**Última atualização:** 11/11/2026, `main` no commit `886e00b`. Os valores da Sprint 4 são os finais da revisão da sprint.

## Painel das sprints

| Métrica | Esperado | Sprint 2 | Sprint 3 | Sprint 4 |
| :-- | :--: | :--: | :--: | :--: |
| **M1.** Cobertura das tabelas de regras por testes | 100% | n/a | 0% | **81,25%** (13/16) |
| **M2.** Aprovação dos testes automatizados | 100% na `main` | 100% (35/35) | 100% (35/35) | 100% (210/210 backend; 47/47 frontend) |
| **M3.** Testes de segurança aprovados | 100% | n/a | n/a | **80%** (4/5) |
| **M4.** Conclusão da sprint | ≥ 80% | **100%** (3/3) | **29%** (2/7) | **100%** (14/14) pelas issues; **85,7%** (12/14) pelos critérios |
| **M5.** Defeitos abertos | 0 críticos | 0 | 0 | 0 críticos; 3 abertos a registrar (1 alto, 2 médios) e 2 corrigidos |

M1 e M3 de Sprints 2 e 3 não se aplicam porque o módulo de regras e o roteiro de testes só passam a existir na Sprint 4.

## Leitura rápida

- **Nenhum defeito crítico.** Todos os testes automatizados passam na CI; os problemas encontrados são de cobertura e de funcionalidade ainda ausente, não de comportamento errado.
- **TI-03 não é atendido:** o check-in não gera nem grava recomendações ([DEF-01](defeitos.md#def-01)). É a pendência mais importante para a Sprint 5.
- **Regras de seleção (R-S2, R-S5 e R-S6) sem cobertura aderente ao Quadro 20**, por divergências que o PO precisa decidir ([matriz](matriz-regras-testes.md)).
- **Critério 3 da seção 2.6** (duas sprints seguidas abaixo de 80%): a Sprint 3 (29%) está abaixo; a Sprint 4 chega a 100% pelas issues e a 85,7% pelos critérios de aceite, então o critério não é acionado.

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
| [Quadro 26 da Sprint 4](quadro-26-sprint-4.md) | Atualização do roteiro de testes aplicada na Visão v2.4. |
| [dados/metricas.csv](dados/metricas.csv) | Todos os valores em formato tabular. |

## Como manter

1. Ao fim de cada sprint, repetir a coleta conforme a [metodologia](metodologia.md) e criar a página `sprint-N.md`.
2. Atualizar a matriz regra × teste sempre que `backend/app/rules/` ou os testes de regras mudarem.
3. Registrar cada defeito como issue `bug` com severidade e atualizar [Defeitos](defeitos.md) com o número da issue.
4. Na revisão da sprint, aplicar o Quadro 26 atualizado em nova versão da Visão (PR na branch `docs`).
