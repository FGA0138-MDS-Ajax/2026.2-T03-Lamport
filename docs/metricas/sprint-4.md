# Sprint 4: Pendências da Sprint 3 e check-in diário (29/10 a 11/11/2026)

**Posição parcial em 10/11/2026** (dia 13 de 14), `main` no commit `faac2cf` e PR #37 aberto. Este registro deve ser reconferido na revisão da sprint (11/11), depois dos merges que ainda ocorrerem. Acompanha a issue #10.

## Métricas

| Métrica | Valor | Esperado | Observação |
| :-- | :--: | :--: | :-- |
| M1. Cobertura das tabelas de regras | **81,25%** (13 de 16), com os testes da branch `test/regras-selecao-rs1-rs3-rs4`, sem merge; 62,5% (10 de 16) na `main` | 100% | R-D e R-A completas; R-S1, R-S3 e R-S4 cobertas; faltam R-S2, R-S5 e R-S6 (decisão do PO). Ver [matriz](matriz-regras-testes.md). |
| M2. Aprovação dos testes automatizados | **100%** (188 de 188 na `main`) | 100% na `main` | [Execução 42691191624](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42691191624). Frontend: 47 de 47. No PR #37: 195 de 195 ([execução 42728982238](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42728982238)). |
| M3. Testes de segurança aprovados | **40%** (2 de 5) | 100% | TS-01 e TS-05 aprovados; TS-02, TS-03 e TS-04 parciais. Nenhum teste reprovado. |
| M4. Conclusão da sprint | **78,6%** (11 de 14) pelo estado das issues; **64,3%** (9 de 14) pelos critérios de aceite | ≥ 80% (referência) | Ver abaixo. |
| M5. Defeitos abertos por severidade | **0** issues `bug` abertas; **5 defeitos propostos**: 0 críticos, 1 alto, 4 médios, 0 baixos | 0 críticos | Ver [Defeitos](defeitos.md). Aguardam a abertura das issues. |

Critério de aceite da issue #10 "nenhum defeito crítico aberto no fim da sprint": **atendido na posição atual**, pois nenhum dos defeitos encontrados é crítico (nenhum teste de segurança falha e nenhuma regra encaminha o usuário de forma errada).

## Roteiro de testes da Sprint 4

Evidência de todos os casos automatizados: execução da CI na `main` indicada acima, salvo onde há outra indicação. "Reparos" cita o PR que corrigiu a falha ou atendeu a revisão.

### Testes unitários

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TU-01 | Aprovado | `test_tu01_*` (soma, todos 0, todos 3, misto, entradas inválidas) | — | 1 | PR #30. |
| TU-02 | Aprovado | `test_tu02_faixas_phq9_limites` e fora da faixa | — | 1 | PR #30. |
| TU-03 | Aprovado | `test_tu03_faixas_gad7_limites` e fora da faixa | — | 1 | PR #30. |
| TU-04 | Aprovado | `test_tu04_caso1` a `caso8`, precedência de R-A1, perfis A a E | — | 1 | PR #30. |
| TU-05 | Aprovado | `test_rd1_*`, `test_thresholds`, `test_unanswered_question_*`, `test_example_from_ti03` | PR #32 | 2 | A revisão do PR #32 pediu a remoção de enums duplicados e de lógica de nível não prevista; atendido antes do merge. |
| TU-06 | **Parcial** | `test_tu06_selecao_limite_zero_ou_catalogo_vazio`, `test_tu06_rs2_ignora_ultimas_exibicoes`, `test_tu06_rs3_match_exato_de_tags` | PR #32 | 2 | Os 3 testes passam, mas não verificam ordem de prioridade, material menos recente, ausência de repetição, máximo de 3, exclusão de inativos nem regra e motivo por item. Ver DEF-02 e DEF-03. |
| TU-07 | **Pendente** | `test_materiais_tu07.py` (4 testes) e `test_seed_materiais.py` (3 testes), no PR #37 | — | 0 | O catálogo não está na `main`. No PR #37 os testes passam ([execução 42728982238](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42728982238)); falta o merge e a conferência dos 7 materiais pelo PO. |

### Testes de integração

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TI-03 | **Não atendido** | `test_ti03_create_checkin_returns_201_with_nivel_and_tags` | PR #23 | 2 | O teste verifica só 201, nível e tags. O resultado esperado do Quadro 26 inclui 2 recomendações persistidas (R-D3 e R-D4), que o sistema não produz: `CheckinService.create` não chama `selecionar_materiais` e não existem `Material` nem `Recomendacao` na `main`. Ver DEF-01. |
| TI-04 | Aprovado | `test_ti04_second_checkin_on_same_day_returns_409` | PR #23 | 2 | Confere 409 e que há um único registro no banco. Uma execução da CI do PR #23 falhou antes da aprovação. |
| TI-05 | **Parcial** | `test_ti05_risk_answer_returns_crise_without_tags` | PR #23 | 2 | Confere 201, nível CRISE e tags vazias. A "lista de recomendações vazia" e "nenhuma linha em Recomendacao" não são verificáveis sem a entidade (DEF-01). |

### Testes de segurança

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TS-01 | Aprovado | `test_ts01_*` (percorre o contrato OpenAPI; 401 sem token e com token malformado) | PR #33 | 2 | A lista pública do teste inclui `GET /api/health` e `GET /api/terms`, além de cadastro e login, e usa `/api/auth/register`. Decisão pendente do PO (issue #22). |
| TS-02 | **Parcial** | `test_me_rejects_expired_token`, `test_me_rejects_token_signed_with_other_key`, `test_ts01_protected_routes_reject_malformed_token` | — | 1 | Falta o caso "token de usuário excluído", que depende da exclusão de conta (R04, Sprint 5). |
| TS-03 | **Parcial** | `test_api_list_checkins_isolation_ts_03`, `test_api_get_checkin_by_id_other_user_returns_404`; no repositório com banco real: `test_get_by_id_other_user_returns_none`, `test_list_by_user_does_not_return_other_users_checkins` | — | 1 | Os testes de API usam repositório falso e sessão simulada, sem PostgreSQL (DEF-05). A parte de avaliações é da Sprint 5. |
| TS-04 | **Parcial** | `test_ts04_*` e o cliente de teste que varre toda resposta JSON da suíte | PR #33 | 2 | Nenhuma chave sensível em nenhuma resposta. Mas `GET /api/users/me` devolve `id`, `email`, `role` e `created_at`; o Quadro 26 exige apenas `id`, `email` e `criado_em`, na rota `/api/me` (issue #22). |
| TS-05 | Aprovado | `test_register_stores_only_password_hash` | — | 1 | Confere o prefixo `$argon2id$`, que o hash difere da senha e que a senha confere com o hash. |

### Resumo do roteiro

| Status | Casos | Quantidade |
| :-- | :-- | :--: |
| Aprovado | TU-01, TU-02, TU-03, TU-04, TU-05, TI-04, TS-01, TS-05 | 8 |
| Parcial | TU-06, TI-05, TS-02, TS-03, TS-04 | 5 |
| Não atendido | TI-03 | 1 |
| Pendente | TU-07 | 1 |
| Não executado | (nenhum previsto para a Sprint 4) | 0 |

São 15 casos. Todos os testes automatizados existentes passam na CI; os casos parciais e não atendidos decorrem de critérios do roteiro que ainda não têm teste ou funcionalidade. A atualização proposta para o Quadro 26 está em [Quadro 26 da Sprint 4](quadro-26-sprint-4.md).

## Conclusão da sprint (M4)

Itens comprometidos conforme a issue #12 (pendências da Sprint 3 e check-in, mais #10 e #11):

| Issue | Item | Estado no GitHub | Critérios de aceite verificados | Contagem pelos critérios |
| :--: | :-- | :--: | :-- | :--: |
| #2 | Protótipo das telas | Fechada | Protótipo no PR #25, ainda aberto na `docs` | Concluído |
| #3 | Vocabulário do check-in | Fechada | PR #14 mesclado | Concluído |
| #4 | Modelo e migração do check-in | Fechada | PR #24 mesclado | Concluído |
| #5 | `POST /api/checkins` e `GET /api/checkins/hoje` | Fechada | Sem recomendações persistidas (TI-03 não atendido) | **Não concluído** |
| #7 | Cliente de API de check-ins | Fechada | PR #26 mesclado | Concluído |
| #8 | Tela de check-in diário | Fechada | PR #31 mesclado | Concluído |
| #10 | Acompanhamento de QA | Aberta | Em andamento | Não concluído |
| #11 | CI e ambiente de demonstração | Fechada | PR #27 mesclado; job `demo` na CI | Concluído |
| #17 | Regras do check-in e seleção | Fechada | TU-06 parcial; M1 em R-S abaixo do exigido na própria issue | **Não concluído** |
| #18 | Regras da avaliação (PHQ-9, GAD-7) | Fechada | PR #30; TU-01 a TU-04 aprovados | Concluído |
| #19 | Catálogo e seed | Aberta | PR #37 com CI verde, sem merge | Não concluído |
| #20 | Tela de Ajuda e botão | Fechada | PR #35; `AjudaPage.test.tsx` | Concluído |
| #21 | Termos de uso | Fechada | PR #36; `PrivacyPage.test.tsx` | Concluído |
| #22 | Pendências da Sprint 2 | Aberta | Sem PR | Não concluído |
| | **Total** | **11 de 14 (78,6%)** | | **9 de 14 (64,3%)** |

As issues #6 e #9 (histórico, R12) não estavam na lista de compromissos da Sprint 4 e foram entregues antes (PR #15 e PR #29); ficam fora do cálculo e contam como adiantamento da Sprint 5.

Em 10/11, a conclusão pelo estado das issues está 1,4 ponto abaixo da referência de 80%. Se o PR #37 for mesclado e a issue #19 aceita até 11/11, o valor sobe para 12 de 14 (85,7%) pelo estado e 10 de 14 (71,4%) pelos critérios. Duas sprints seguidas abaixo de 80% acionam o critério 3 da seção 2.6: a Sprint 3 (29%) já está abaixo e a Sprint 4 ficará abaixo se não chegar a 80%; ver [Sprint 3](sprint-3.md).

## Integração contínua na sprint

| Evento | Execuções | Aprovadas | Reprovadas | Canceladas |
| :-- | :--: | :--: | :--: | :--: |
| Pull request | 32 | 23 | 9 | 0 |
| Push (`main` e `developer`) | 16 | 15 | 0 | 1 |

Das 32 execuções em PR, 9 (28%) falharam; todas as falhas foram corrigidas antes do merge, ou seja, a CI cumpriu a função de bloquear código com erro. Os PRs #32 (3 falhas) e #29 (3 falhas) concentraram as reprovações; os PRs #23, #26 e #31 tiveram uma falha cada.

## Conferência dos PRs

A conferência de cada issue prevista na #10 está em [Conferência dos PRs](conferencia-prs-sprint-4.md).

## Pendências até a revisão da sprint (11/11)

1. Abrir as issues dos defeitos propostos, com a label `bug` e a severidade (aguarda confirmação).
2. Acompanhar o merge do PR #37 e reexecutar a conferência do TU-07.
3. Reconferir a matriz regra × teste depois de qualquer alteração em `app/rules/`.
4. Na revisão: aplicar a [atualização do Quadro 26](quadro-26-sprint-4.md) em nova versão da Visão, por PR na branch `docs`, e registrar M1 a M5 finais.
