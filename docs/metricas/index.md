# Métricas e qualidade

Registro do acompanhamento de qualidade feito pelo QA (issues #10 e #62), com as métricas M1 a M5 do GQM (Visão, seção 5, Quadro 23) de cada sprint, o status dos casos do roteiro de testes (Quadro 26) e os defeitos encontrados.

**Última atualização:** 25/11/2026, às 22h55 (fim da Sprint 5), `main` no commit `22bf6a4` (PR #80). Os valores da Sprint 4 são os finais da revisão daquela sprint.

## Painel das sprints

| Métrica | Esperado | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 |
| :-- | :--: | :--: | :--: | :--: | :--: |
| **M1.** Cobertura das tabelas de regras por testes | 100% | n/a | 0% | **75%** (12/16) | **100%** (16/16) |
| **M2.** Aprovação dos testes automatizados | 100% na `main` | 100% (35/35) | 100% (35/35) | 100% (210/210 backend; 47/47 frontend) | 100% (298/298 backend; 85/85 frontend) |
| **M3.** Testes de segurança aprovados | 100% | n/a | n/a | **80%** (4/5) | **100%** (5/5) |
| **M4.** Conclusão da sprint | ≥ 80% | **100%** (3/3) | **29%** (2/7) | **100%** (14/14) pelas issues; **85,7%** (12/14) pelos critérios | **93,8%** (15/16) |
| **M5.** Defeitos abertos | 0 críticos | 0 | 0 | 0 críticos; 3 abertos, #45 a #47 (1 alto, 2 médios), e 2 corrigidos | 0 críticos; 0 issues `bug` abertas; 5 defeitos novos (2 altos, 2 médios, 1 baixo), 1 aberto (médio); #45 a #47 corrigidos |

M1 e M3 de Sprints 2 e 3 não se aplicam porque o módulo de regras e o roteiro de testes só passam a existir na Sprint 4.

## Leitura rápida

- **Sprint 5: os 24 casos do roteiro aprovados.** M1 e M3 chegam a 100%, todos os automatizados passam (inclusive TI-06 e TI-07) e, no ciclo 1 do roteiro de sistema, TSI-01 a TSI-04 e o TSI-05 (antecipado) foram aprovados pela interface. O único defeito aberto é o [DEF-08](defeitos.md#def-08) (médio): o ambiente de demonstração sobe sem o catálogo.
- **M4 da Sprint 5 em 93,8%** (15 de 16), acima da referência de 80%. Todas as issues de desenvolvimento foram entregues; só a #63, do PO, segue aberta.
- **As entregas da Sprint 5 estão na `main`** desde o PR #80 (25/11, 22h50), com a CI aprovada.
- **Nenhum defeito crítico.** A jornada de risco (TSI-02) e a Ajuda Imediata sem login (TSI-04) foram aprovadas no navegador.
- **O site da documentação ficou sem publicar** entre o merge do PR #65 e o commit `eedab0a` (marcadores de conflito no `mkdocs.yml`, [DEF-09](defeitos.md#def-09), já corrigido).

## Páginas

| Página | Conteúdo |
| :-- | :-- |
| [Metodologia](metodologia.md) | Definição de cada métrica, fontes, status dos casos e limitações da coleta. |
| [Sprint 2](sprint-2.md) | Métricas e itens da Sprint 2 (registro retroativo). |
| [Sprint 3](sprint-3.md) | Métricas e itens da Sprint 3 (registro retroativo). |
| [Sprint 4](sprint-4.md) | Métricas, status dos 15 casos do roteiro, conclusão e CI da Sprint 4. |
| [Sprint 5](sprint-5.md) | Métricas, casos do roteiro, ciclo 1 do roteiro de sistema (TSI-01 a TSI-04) com capturas, conclusão e CI da Sprint 5. |
| [Matriz regra × teste](matriz-regras-testes.md) | M1: cada linha de R-D, R-A e R-S e o teste que a cobre. |
| [Conferência dos PRs da Sprint 4](conferencia-prs-sprint-4.md) | Issues #5, #6, #17, #18, #19 e #22: casos existentes, rodando na CI e lacunas. |
| [Conferência dos PRs da Sprint 5](conferencia-prs-sprint-5.md) | PRs #65 a #78 contra o Quadro 26 e os critérios de aceite; issues sem PR. |
| [Defeitos](defeitos.md) | DEF-01 a DEF-10, com severidade, situação e issue de cada um. |
| [Quadro 26 da Sprint 4](quadro-26-sprint-4.md) | Atualização do roteiro de testes aplicada na Visão v2.4 e corrigida na v2.5. |
| [Quadro 26 da Sprint 5](quadro-26-sprint-5.md) | Atualização do roteiro de testes proposta na Visão v2.9. |
| [dados/metricas.csv](dados/metricas.csv) | Todos os valores em formato tabular. |

## Como manter

1. Ao fim de cada sprint, repetir a coleta conforme a [metodologia](metodologia.md) e criar a página `sprint-N.md`.
2. Atualizar a matriz regra × teste sempre que `backend/app/rules/` ou os testes de regras mudarem.
3. Registrar cada defeito como issue `bug` com severidade e atualizar [Defeitos](defeitos.md) com o número da issue.
4. Na revisão da sprint, aplicar o Quadro 26 atualizado em nova versão da Visão (PR na branch `docs`).
