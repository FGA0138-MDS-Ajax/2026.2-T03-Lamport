# Sprint 3: Regras e catálogo (15/10 a 28/10/2026)

Registro retroativo, feito a partir do histórico do GitHub e do replanejamento da Visão v2.2. Entregáveis do Quadro 8: Visão e Arquitetura v2.1; módulo de regras com TU-01 a TU-07; catálogo inicial (R13); termos (R03); Tela de Ajuda e botão (R10 no frontend, R11); CI executando os testes; pendências da Sprint 2.

## Métricas

| Métrica | Valor | Observação |
| :-- | :--: | :-- |
| M1. Cobertura das tabelas de regras | **0%** (0 de 16) | A `main` de 26/10 (`2d207b6`) não continha o módulo de regras nem testes de regras. |
| M2. Aprovação dos testes automatizados | **100%** (35 de 35 no pytest) | Última execução na `main` da sprint (26/10): [execução 40416931338](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/40416931338). Nenhum teste novo na sprint. Frontend: 20 de 20. |
| M3. Testes de segurança aprovados | n/a | TS-01 a TS-05 ainda não existiam. |
| M4. Conclusão da sprint | **29%** (2 de 7 itens) | Ver abaixo. Valor abaixo da referência de 80%. |
| M5. Defeitos abertos por severidade | 0 críticos, 0 altos, 0 médios, 0 baixos | Nenhuma issue `bug` foi aberta no período. |

## Itens comprometidos (M4)

| Item | Situação | Evidência |
| :-- | :--: | :-- |
| Visão e Arquitetura v2.1 | Concluído | Publicadas em 27/10 (commit `2987dfb`). |
| CI executando os testes | Concluído | Workflow `tests.yml` desde 13/10, executado em todos os PRs. |
| Módulo de regras com TU-01 a TU-07 | Não concluído | Passou à Sprint 4 (v2.2). |
| Catálogo inicial (R13) | Não concluído | Passou à Sprint 4 (v2.2). |
| Termos (R03) | Não concluído | Passou à Sprint 4 (v2.2). |
| Tela de Ajuda e botão (R10 no frontend, R11) | Não concluído | Passou à Sprint 4 (v2.2). |
| Pendências da Sprint 2 | Não concluído | Passou à Sprint 4 (v2.2). |

A lista de itens não concluídos coincide com a descrição do replanejamento na Visão v2.2 (seção 2.6, critério 1).

## Integração contínua

| Evento | Execuções | Aprovadas | Reprovadas |
| :-- | :--: | :--: | :--: |
| Pull request | 1 | 1 | 0 |
| Push (`main`) | 1 | 1 | 0 |

Só um PR passou pela CI na sprint (o PR #13, `developer` para `main`, em 26/10). A baixa quantidade de execuções reflete a pouca atividade de código no período, e não um processo mais estável.

## Análise

- **Critério 3 da seção 2.6 (atenção).** Duas sprints seguidas abaixo de 80% exigem reduzir a capacidade planejada. A Sprint 2 ficou em 100%, então o critério não foi acionado aqui; ele seria acionado se a Sprint 4 também ficasse abaixo de 80%, o que não ocorreu: a Sprint 4 fechou com 100% pelo estado das issues e 85,7% pelos critérios de aceite ([Sprint 4](sprint-4.md)).
- O risco R6 (atraso em itens Must) se concretizou: cinco dos sete itens da sprint foram para a Sprint 4.
- O valor de M1 em 0% na Sprint 3 mostra que o plano de colocar as regras antes das telas (seção 2.1 da Visão) não se cumpriu nessa sprint.
