# Quadro 26: atualização proposta na Sprint 5

As colunas de acompanhamento (Status, Evidência, Reparos e Ciclos) do Quadro 26 foram atualizadas na **Visão v2.9** (25/11/2026), depois da v2.8 do PO (PR #79: catálogo conferido e retrospectiva da Sprint 4, sem mudança no Quadro 26), pelo mesmo PR na branch `docs` que registra estas métricas (issue #62). A versão passa a valer quando o PO aprova e mescla o PR. O Quadro 26 da [Visão](../visao-produto-projeto.md) é a fonte; esta página resume o que mudou.

Evidência dos casos automatizados: [execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093) da CI na `main` (commit `22bf6a4`, PR #80): 298 testes no backend e 54 no frontend, todos aprovados, e o job `demo` aprovado. Evidência dos casos de sistema: [ciclo 1](sprint-5.md#roteiro-de-sistema-ciclo-1), com capturas de tela.

## O que mudou em relação às v2.7 e v2.8

| Caso | v2.7 e v2.8 (Sprint 4) | v2.9 (Sprint 5) | Reparos | Ciclos |
| :-- | :-- | :-- | :--: | :--: |
| TU-06 | Parcial | **Aprovado** | PR #32, #38 e #66 | 2 → 3 |
| TI-03 | Não atendido | **Aprovado** | PR #23 e #67 | 2 → 3 |
| TI-05 | Parcial | **Aprovado** | PR #23 e #67 | 2 → 3 |
| TI-06 | Não executado | **Aprovado** | — | 0 → 1 |
| TI-07 | Não executado | **Aprovado** | — | 0 → 1 |
| TS-03 | Parcial | **Aprovado** | PR #39 e #70 | 2 → 3 |
| TSI-01 | Não executado | **Aprovado** (não atendido na execução 1, DEF-06) | PR #71 | 0 → 5 |
| TSI-02 | Não executado | **Aprovado** | — | 0 → 5 |
| TSI-03 | Não executado | **Aprovado** (sem telas nas execuções 1 e 2 e só com a de resultado na 3, DEF-07) | PR #75 e #77 | 0 → 5 |
| TSI-04 | Não executado | **Aprovado** | — | 0 → 5 |
| TSI-05 | Não executado | **Aprovado** (antecipado da Sprint 6, para o aceite da #61) | — | 0 → 3 |

Nos demais casos aprovados (TU-01 a TU-05, TU-07, TI-01, TI-02, TI-04, TS-01, TS-02, TS-04 e TS-05), só a evidência mudou, para a execução da CI da Sprint 5; no TS-02, o caso do usuário excluído passa a usar a exclusão real (reparo PR #73). O TSI-05 é da Sprint 6, mas foi executado na Sprint 5 e será repetido no ciclo final.

## Resultado por caso

| Status | Casos | Quantidade |
| :-- | :-- | :--: |
| Aprovado | TU-01 a TU-07, TI-01 a TI-07, TS-01 a TS-05, TSI-01 a TSI-05 | 24 |

## Fora desta versão da Visão

| Onde | Situação |
| :-- | :-- |
| Quadro 8, coluna "% concl." | Não alterada. Quem registra é o PO. Valor sugerido pelo QA, arredondado para baixo ao múltiplo de 10%, como na v2.6: Sprint 5, **90%** (15 de 16, ou 93,8%, pelo estado das issues e pelos critérios de aceite); 100% se a #63 fechar antes do registro. |
| Replanejamento (seção 2.6) | Nenhum critério é acionado: todos os Must da sprint foram entregues e a conclusão ficou acima de 80%. |
| Quadro 25 | Atendido no fim da sprint: o PR #80 levou as entregas à `main`, a CI da `main` passou, e a execução final do roteiro de sistema usou um commit de conteúdo idêntico ao da `main`. Nas Sprints 6 em diante, o ideal é rodar o roteiro já sobre a `main`. |
| PDF da Visão | Os PDFs ABNT da v2.8 e da v2.9 ainda não foram gerados. |
