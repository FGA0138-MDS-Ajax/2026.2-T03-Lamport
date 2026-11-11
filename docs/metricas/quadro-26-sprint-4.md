# Quadro 26: atualização proposta para a Sprint 4

Proposta de preenchimento das colunas de acompanhamento do Quadro 26 da Visão (Status, Evidência, Reparos e Ciclos) para os casos da Sprint 4, com a posição de 10/11/2026.

!!! warning "Ainda não aplicado à Visão"
    A Visão v2.2 continua como está. A issue #10 manda atualizar o Quadro 26 **na revisão da sprint**, em nova versão da Visão, por PR na branch `docs`. Esta página é o rascunho pronto para essa atualização; os valores devem ser reconferidos em 11/11, depois dos merges que ainda ocorrerem (em especial o PR #37). O texto sobre "resultados obtidos" da seção 6.1, item 5, e a legenda da seção 6.2 ("atualmente Não executado") também precisam ser ajustados na ocasião.

Evidência dos casos automatizados: [execução 42691191624](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42691191624) da CI na `main` (commit `faac2cf`), 188 testes aprovados no backend e 47 no frontend.

| ID | Status | Evidência | Reparos | Ciclos |
| :-- | :-- | :-- | :--: | :--: |
| TU-01 | Aprovado | [CI 42691191624](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42691191624); `test_rules_avaliacao.py` | — | 1 |
| TU-02 | Aprovado | idem | — | 1 |
| TU-03 | Aprovado | idem | — | 1 |
| TU-04 | Aprovado | idem | — | 1 |
| TU-05 | Aprovado | CI 42691191624; `test_rules_checkin.py` | PR #32 | 2 |
| TU-06 | Parcial: os 3 testes passam, mas o resultado esperado do Quadro não é verificado (DEF-02 e DEF-03) | CI 42691191624; `test_rules_checkin.py` | PR #32 | 2 |
| TU-07 | Pendente: aprovado no PR #37, ainda sem merge | [CI 42728982238](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42728982238) (PR #37) | — | 0 |
| TI-03 | Não atendido: sem recomendações persistidas (DEF-01) | CI 42691191624; `test_checkins.py` (verifica só 201, nível e tags) | PR #23 | 2 |
| TI-04 | Aprovado | CI 42691191624; `test_checkins.py` | PR #23 | 2 |
| TI-05 | Parcial: sem a verificação de recomendações (DEF-01) | CI 42691191624; `test_checkins.py` | PR #23 | 2 |
| TS-01 | Aprovado | CI 42691191624; `test_security.py` | PR #33 | 2 |
| TS-02 | Parcial: falta o token de usuário excluído (R04, Sprint 5) | CI 42691191624; `test_auth.py`, `test_security.py` | — | 1 |
| TS-03 | Parcial: API sem banco (DEF-05); avaliações na Sprint 5 | CI 42691191624; `test_checkins_get.py`, `test_checkin_repository.py` | — | 1 |
| TS-04 | Parcial: rota e campos de `/api/me` diferentes do Quadro (DEF-04) | CI 42691191624; `test_security.py`, `conftest.py` | PR #33 | 2 |
| TS-05 | Aprovado | CI 42691191624; `test_register.py` | — | 1 |

Os casos TI-01 e TI-02 (Sprint 2, replanejados como pendência na #22) devem ser registrados junto: TI-02 **Aprovado** (`test_auth.py`) e TI-01 **Parcial** (`test_register.py` não verifica a declaração 18+, que não existe; DEF-04).

## Outras atualizações previstas para a mesma versão da Visão

| Onde | Atualização |
| :-- | :-- |
| Quadro 8, coluna "% concl." | Sprint 2: 100% (3 de 3 itens). Sprint 3: 30% (2 de 7). Sprint 4: valor da revisão. Percentuais em intervalos de 10%, conforme a seção 2.3. Quem registra é o PO (issue #12). |
| Seção 5 | Registrar M1 a M5 finais da Sprint 4 ([Sprint 4](sprint-4.md)). |
| Quadro 20 | Somente se o PO decidir pela alteração das regras R-S2, R-S5 ou R-S6 (DEF-02). |
| Histórico de revisões e [Histórico de versões](../historico-versoes.md) | Nova linha com a versão, a data e a descrição da atualização. |
