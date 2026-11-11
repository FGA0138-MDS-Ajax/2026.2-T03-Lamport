# Quadro 26: atualização aplicada na Sprint 4

Os valores das colunas de acompanhamento (Status, Evidência, Reparos e Ciclos) dos casos previstos até a Sprint 4 foram **aplicados à Visão na versão 2.4** (11/11/2026), por PR na branch `docs`, conforme a issue #10. O Quadro 26 da [Visão](../visao-produto-projeto.md) é a fonte; esta página resume o resultado e o que ficou fora.

Evidência dos casos automatizados: [execução 43118733055](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43118733055) da CI na `main` (commit `886e00b`): 210 testes no backend e 47 no frontend, todos aprovados, e o job `demo` aprovado.

## Resultado por caso

| Status | Casos | Quantidade |
| :-- | :-- | :--: |
| Aprovado | TU-01 a TU-05, TU-07, TI-01, TI-02, TI-04, TS-01, TS-02, TS-04, TS-05 | 13 |
| Parcial | TU-06, TI-05, TS-03 | 3 |
| Não atendido | TI-03 | 1 |
| Não executado | TI-06, TI-07 e TSI-01 a TSI-05 (Sprints 5 e 6) | 7 |

Os 17 casos previstos até a Sprint 4 são TU-01 a TU-07, TI-01 a TI-05 e TS-01 a TS-05.

## Pontos que ficaram parciais ou não atendidos

| Caso | Motivo | Defeito |
| :-- | :-- | :--: |
| TU-06 | Os testes não verificam exclusão de inativos nem regra e motivo por item; R-S2, R-S5 e R-S6 divergem do Quadro 20 (decisão do PO). | [DEF-02](defeitos.md#def-02), [DEF-03](defeitos.md#def-03) |
| TI-03 | O check-in não gera nem grava recomendações. | [DEF-01](defeitos.md#def-01) |
| TI-05 | Sem a entidade `Recomendacao`, não há como verificar a lista vazia e a ausência de linhas. | [DEF-01](defeitos.md#def-01) |
| TS-03 | A parte de check-ins está aprovada no banco de teste; a de avaliações depende do endpoint da Sprint 5 (o roteiro marca o caso como S4–S5). | DEF-05 corrigido |

## Fora desta versão da Visão

| Onde | Situação |
| :-- | :-- |
| Quadro 8, coluna "% concl." | Não alterada. Quem registra é o PO (issue #12). Valores sugeridos pelo QA, em intervalos de 10%: Sprint 2, 100% (3 de 3); Sprint 3, 30% (2 de 7); Sprint 4, 100% (14 de 14 pelo estado das issues, com a #10 fechada pelo PR das métricas; 85,7% pelos critérios de aceite). |
| Seção 5 da Visão | Os valores de M1 a M5 da Sprint 4 estão em [Sprint 4](sprint-4.md). |
| Quadro 20 | Só muda se o PO decidir alterar R-S2, R-S5 ou R-S6 ([DEF-02](defeitos.md#def-02)). |
