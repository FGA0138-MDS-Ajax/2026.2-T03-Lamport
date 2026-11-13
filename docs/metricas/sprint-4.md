# Sprint 4: Pendências da Sprint 3 e check-in diário (29/10 a 11/11/2026)

**Posição final em 11/11/2026** (dia 14 de 14), `main` no commit `886e00b` (PR #44), com todos os PRs da sprint mesclados e a CI da `main` verde ([execução 43118733055](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43118733055)). Acompanha a issue #10.

## Métricas

| Métrica | Valor | Esperado | Observação |
| :-- | :--: | :--: | :-- |
| M1. Cobertura das tabelas de regras | **75%** (12 de 16) | 100% | R-D e R-A completas; R-S3 e R-S4 cobertas (PR #38). R-S1 tem teste, mas o código não inclui AJUDA_PROFISSIONAL na ordem de prioridade; R-S2, R-S5 e R-S6 dependem de decisão do PO ([DEF-02](defeitos.md#def-02)). Ver [matriz](matriz-regras-testes.md). |
| M2. Aprovação dos testes automatizados | **100%** (210 de 210 no backend; 47 de 47 no frontend) | 100% na `main` | [Execução 43118733055](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43118733055), `main` no commit `886e00b`; jobs `backend`, `frontend` e `demo` aprovados. |
| M3. Testes de segurança aprovados | **80%** (4 de 5) | 100% | TS-01, TS-02, TS-04 e TS-05 aprovados. TS-03 parcial: a parte de check-ins está coberta no banco de teste, e a de avaliações depende do endpoint da Sprint 5 (o roteiro marca o caso como S4–S5). Nenhum teste reprovado. |
| M4. Conclusão da sprint | **100%** (14 de 14) pelo estado das issues; **85,7%** (12 de 14) pelos critérios de aceite | ≥ 80% (referência) | A #10 é contada como concluída, pois é fechada pelo PR com estes registros. Ver abaixo. |
| M5. Defeitos abertos por severidade | **3** issues `bug` abertas (#45, #46 e #47): 0 críticos, 1 alto, 2 médios, 0 baixos; 2 defeitos corrigidos na sprint | 0 críticos | Ver [Defeitos](defeitos.md). |

Critério de aceite da issue #10 "nenhum defeito crítico aberto no fim da sprint": **atendido**, pois nenhum dos defeitos encontrados é crítico (nenhum teste de segurança falha e nenhuma regra em uso encaminha o usuário de forma errada; a seleção de conteúdo, onde está a divergência de R-S1, ainda não é chamada pelo sistema, ver [DEF-02](defeitos.md#def-02)).

## Roteiro de testes da Sprint 4

Evidência de todos os casos automatizados: [execução 43118733055](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43118733055) da CI na `main`, salvo onde há outra indicação. "Reparos" cita o PR que corrigiu a falha ou atendeu a revisão.

### Testes unitários

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TU-01 | Aprovado | `test_tu01_*` (soma, todos 0, todos 3, misto, entradas inválidas) | — | 1 | PR #30. |
| TU-02 | Aprovado | `test_tu02_faixas_phq9_limites` e fora da faixa | — | 1 | PR #30. |
| TU-03 | Aprovado | `test_tu03_faixas_gad7_limites` e fora da faixa | — | 1 | PR #30. |
| TU-04 | Aprovado | `test_tu04_caso1` a `caso8`, precedência de R-A1, perfis A a E | — | 1 | PR #30. |
| TU-05 | Aprovado | `test_rd1_*`, `test_thresholds`, `test_unanswered_question_*`, `test_example_from_ti03` | PR #32 | 2 | A revisão do PR #32 pediu a remoção de enums duplicados e de lógica de nível não prevista; atendido antes do merge. |
| TU-06 | **Parcial** | `test_tu06_*` (7 testes: limite zero e catálogo vazio, R-S1, R-S2, dois de R-S3 e dois de R-S4) | PR #32 e PR #38 | 2 | Os 7 testes passam e verificam a ordem de prioridade (só com as tags do check-in), a ausência de repetição e o máximo de 3. Não verificam a ordem com AJUDA_PROFISSIONAL, que o código não inclui, o material menos recente, a exclusão de inativos nem a regra e o motivo por item. Ver DEF-02 e DEF-03. |
| TU-07 | Aprovado | `test_materiais_tu07.py` (4 testes) e `test_seed_materiais.py` (4 testes) | PR #37 | 1 | Catálogo na `main` com 7 materiais oficiais. Resta a conferência dos 7 materiais pelo PO, prevista na lista de aceite do PR #37. |

### Testes de integração

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TI-03 | **Não atendido** | `test_ti03_create_checkin_returns_201_with_nivel_and_tags` | PR #23 | 2 | O teste verifica só 201, nível e tags. O resultado esperado do Quadro 26 inclui 2 recomendações persistidas (R-D3 e R-D4), que o sistema não produz: `CheckinService.create` não chama `selecionar_materiais` e não existe `Recomendacao` (o modelo `Material` entrou com o PR #37). Ver DEF-01. |
| TI-04 | Aprovado | `test_ti04_second_checkin_on_same_day_returns_409` | PR #23 | 2 | Confere 409 e que há um único registro no banco. Uma execução da CI do PR #23 falhou antes da aprovação. |
| TI-05 | **Parcial** | `test_ti05_risk_answer_returns_crise_without_tags` | PR #23 | 2 | Confere 201, nível CRISE e tags vazias. A "lista de recomendações vazia" e "nenhuma linha em Recomendacao" não são verificáveis sem a entidade (DEF-01). |

### Testes de segurança

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TS-01 | Aprovado | `test_ts01_*` (percorre o contrato OpenAPI; 401 sem token e com token malformado) | PR #33 e PR #39 | 3 | A lista pública é a da Visão v2.3: `/api/auth/cadastro`, `/api/auth/login`, `/api/terms` e `/api/health`. O Quadro 26 diz que o teste percorre `app.routes`, mas ele percorre o contrato OpenAPI. Hoje as duas listas coincidem; uma rota marcada com `include_in_schema=False` não seria verificada. |
| TS-02 | Aprovado | `test_me_rejects_expired_token`, `test_me_rejects_token_signed_with_other_key`, `test_ts01_protected_routes_reject_malformed_token`, `test_me_rejects_token_of_deleted_user` | PR #39 | 2 | Os quatro casos do roteiro retornam 401. O usuário excluído é removido diretamente no banco do teste, pois a rota de exclusão de conta (R04) é da Sprint 5. |
| TS-03 | **Parcial** | `test_ts03_isolamento.py` (5 testes com o `client` e o banco de teste); `test_api_list_checkins_isolation_ts_03`, `test_api_get_checkin_by_id_other_user_returns_404`; no repositório: `test_get_by_id_other_user_returns_none`, `test_list_by_user_does_not_return_other_users_checkins` | PR #39 | 2 | O isolamento de check-ins está coberto no banco de teste (DEF-05 corrigido). Falta a parte de avaliações (`GET /api/avaliacoes/{id}`), do escopo da Sprint 5; o roteiro marca o TS-03 como S4–S5. |
| TS-04 | Aprovado | `test_ts04_*` e o cliente de teste que varre toda resposta JSON da suíte | PR #33 e PR #39 | 3 | Nenhuma chave sensível em nenhuma resposta; `GET /api/me` devolve só `id`, `email` e `criado_em`. |
| TS-05 | Aprovado | `test_register_stores_only_password_hash` | — | 1 | Confere o prefixo `$argon2id$`, que o hash difere da senha e que a senha confere com o hash. |

### Resumo do roteiro

| Status | Casos | Quantidade |
| :-- | :-- | :--: |
| Aprovado | TU-01, TU-02, TU-03, TU-04, TU-05, TU-07, TI-04, TS-01, TS-02, TS-04, TS-05 | 11 |
| Parcial | TU-06, TI-05, TS-03 | 3 |
| Não atendido | TI-03 | 1 |
| Não executado | (nenhum previsto para a Sprint 4) | 0 |

São 15 casos. Todos os testes automatizados existentes passam na CI. Os casos parciais e o não atendido decorrem de critérios do roteiro que ainda não têm teste ou funcionalidade: recomendações persistidas (TI-03 e TI-05), verificações do TU-06 e a parte de avaliações do TS-03. Os casos TI-01 e TI-02 (Sprint 2, pendências da #22) também estão **aprovados**: TI-01 com a declaração 18+ (422 sem ela) e TI-02 com o limite de tentativas de login. A atualização do Quadro 26 está em [Quadro 26 da Sprint 4](quadro-26-sprint-4.md).

## Conclusão da sprint (M4)

Itens comprometidos conforme a issue #12 (pendências da Sprint 3 e check-in, mais #10 e #11):

| Issue | Item | Estado no GitHub | Critérios de aceite verificados | Contagem pelos critérios |
| :--: | :-- | :--: | :-- | :--: |
| #2 | Protótipo das telas | Fechada | Link do Figma anexado na issue (12/11); telas exportadas no PR #25, ainda aberto na `docs` | Concluído |
| #3 | Vocabulário do check-in | Fechada | PR #14 mesclado | Concluído |
| #4 | Modelo e migração do check-in | Fechada | PR #24 mesclado | Concluído |
| #5 | `POST /api/checkins` e `GET /api/checkins/hoje` | Fechada | Sem recomendações persistidas (TI-03 não atendido) | **Não concluído** |
| #7 | Cliente de API de check-ins | Fechada | PR #26 mesclado | Concluído |
| #8 | Tela de check-in diário | Fechada | PR #31 mesclado | Concluído |
| #10 | Acompanhamento de QA | Fechada pelo PR destas métricas na `docs` | Quadro 26 atualizado (Visão v2.4); M1 a M5 registradas; nenhum defeito crítico aberto; defeitos documentados | Concluído |
| #11 | CI e ambiente de demonstração | Fechada | PR #27 mesclado; job `demo` na CI | Concluído |
| #17 | Regras do check-in e seleção | Fechada | TU-06 parcial; M1 em R-S abaixo do exigido na própria issue | **Não concluído** |
| #18 | Regras da avaliação (PHQ-9, GAD-7) | Fechada | PR #30; TU-01 a TU-04 aprovados | Concluído |
| #19 | Catálogo e seed | Fechada | PR #37 mesclado; TU-07 aprovado; conferência dos 7 materiais pelo PO pendente | Concluído |
| #20 | Tela de Ajuda e botão | Fechada | PR #35; `AjudaPage.test.tsx` | Concluído |
| #21 | Termos de uso | Fechada | PR #36; `PrivacyPage.test.tsx` | Concluído |
| #22 | Pendências da Sprint 2 | Fechada | PRs #39, #41 e #42 mesclados; decisões do PO na Visão e Arquitetura v2.3 (PR #40); TI-01, TI-02, TS-01, TS-02, TS-04 e TS-05 aprovados | Concluído |
| | **Total** | **14 de 14 (100%)** | | **12 de 14 (85,7%)** |

As issues #6 e #9 (histórico, R12) não estavam na lista de compromissos da Sprint 4 e foram entregues antes (PR #15 e PR #29); ficam fora do cálculo e contam como adiantamento da Sprint 5.

Pelo estado das issues, a Sprint 4 fecha com 14 de 14 (100%), acima da referência de 80%. Pelos critérios de aceite, são 12 de 14 (85,7%), também acima da referência. As duas issues que seguem "Não concluídas" pelos critérios, embora fechadas no GitHub, são a #5 (recomendações não persistidas, TI-03) e a #17 (TU-06 parcial e M1 das regras R-S abaixo do exigido na própria issue). A #10 é contada como concluída porque o PR que registra estas métricas é o que a fecha.

Com a Sprint 4 acima de 80% nas duas leituras, o critério 3 da seção 2.6 (duas sprints seguidas abaixo de 80%) não é acionado, apesar de a Sprint 3 (29%) ter ficado abaixo. Ver [Sprint 3](sprint-3.md).

## Integração contínua na sprint

| Evento | Execuções | Aprovadas | Reprovadas | Canceladas |
| :-- | :--: | :--: | :--: | :--: |
| Pull request | 38 | 28 | 10 | 0 |
| Push (`main` e `developer`) | 23 | 21 | 1 | 1 |

Das 38 execuções em PR, 10 (26%) falharam, e todas essas falhas foram corrigidas antes do merge. Os PRs #32 (3 falhas) e #29 (3 falhas) concentraram as reprovações; os PRs #23, #26, #31 e #39 tiveram uma falha cada. A falha em push foi na `developer`, depois do merge do PR #41, que deixou o job `demo` com o campo antigo `password` ([execução 43114251359](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43114251359)); o PR #42 corrigiu. Os PRs #41 e #42 eram correções das pendências da #22, acompanhadas pelo PO, e foram mesclados sem execução da CI no PR.

## Conferência dos PRs

A conferência de cada issue prevista na #10 está em [Conferência dos PRs](conferencia-prs-sprint-4.md).

## Pendências após a revisão da sprint

1. Tratar as issues dos defeitos abertos: #45 (DEF-01, alta), #46 (DEF-02, média; R-S2, R-S5 e R-S6 dependem do PO) e #47 (DEF-03, média); DEF-04 e DEF-05 foram corrigidos na própria sprint.
2. Integrar as recomendações ao check-in (DEF-01): modelo e migração de `Recomendacao`, chamada a `selecionar_materiais` e resposta de `POST /api/checkins`.
3. PO decidir R-S2, R-S5 e R-S6 (DEF-02) e conferir os 7 materiais do catálogo.
4. Corrigir R-S1 no código (ordem de prioridade com AJUDA_PROFISSIONAL, como no Quadro 20) e completar o TU-06 (essa ordem, exclusão de inativos, regra e motivo por item) e o teto de 2 para N2, antes de ligar a seleção à avaliação (Sprint 5).
5. Sprint 5: parte de avaliações do TS-03, junto de `GET /api/avaliacoes`.
6. Reconferir a matriz regra × teste depois de qualquer alteração em `app/rules/`.
7. Fazer o TS-01 percorrer `app.routes`, como diz o Quadro 26, ou o PO atualizar o Quadro.
