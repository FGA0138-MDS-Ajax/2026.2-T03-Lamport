# Conferência dos PRs da Sprint 4

Tarefa da issue #10: conferir, nos PRs das issues #5, #6, #17, #18, #19 e #22, que cada caso do roteiro previsto para a Sprint 4 existe e roda na CI, e apontar as lacunas. Posição de 10/11/2026.

**Os comentários abaixo não foram publicados nos PRs.** Estão escritos para que o QA os poste (ou os transforme em issues, ver [Defeitos](defeitos.md)) quando decidir.

## Resumo

| Issue | PR | Casos | Existem e rodam na CI? | Lacuna |
| :--: | :--: | :-- | :--: | :-- |
| #5 | #23 (mesclado) | TI-03, TI-04, TI-05 | Sim, os três | TI-03 e TI-05 não verificam recomendações; funcionalidade ausente (DEF-01) |
| #6 | #15 (mesclado) | TS-03 (check-ins) | Sim | Testes de API sem banco (DEF-05); parte de avaliações é da Sprint 5 |
| #17 | #32 e #33 (mesclados) | TU-05, TU-06 | Sim | TU-06 sem verificação de R-S1, R-S3, R-S4; divergências do Quadro 20 (DEF-02, DEF-03) |
| #18 | #30 (mesclado) | TU-01 a TU-04 | Sim, sem lacuna | Nenhuma |
| #19 | #37 (aberto) | TU-07 | Sim, no PR; não na `main` | Falta merge e a conferência dos materiais pelo PO |
| #22 | sem PR | TI-01, TI-02, TS-01, TS-02, TS-04, TS-05 | TI-02, TS-01, TS-02 (parcial), TS-04 (parcial) e TS-05 sim; TI-01 não nos termos do roteiro | Contrato do cadastro e de `/api/me` (DEF-04); decisões do PO pendentes |

## #5, PR #23: `POST /api/checkins` e `GET /api/checkins/hoje`

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| TI-03: 201, tags [ANSIEDADE, SONO], 2 recomendações com R-D3 e R-D4 | `test_ti03_create_checkin_returns_201_with_nivel_and_tags` | **Falta a parte das recomendações** |
| TI-04: 409 e nenhum registro novo | `test_ti04_second_checkin_on_same_day_returns_409` | Atendido |
| TI-05: CRISE, sem recomendações, sem linha em `Recomendacao` | `test_ti05_risk_answer_returns_crise_without_tags` | **Parcial** (a entidade não existe) |
| Check-in só com P5 respondida → 201 | `test_only_p5_is_required` | Atendido |
| 422 fora da faixa ou sem `p5` | `test_invalid_values_return_422`, `test_missing_p5_returns_422` | Atendido |
| `GET /api/checkins/hoje` → 200 ou 404 | `test_today_returns_checkin_of_the_day`, `test_today_returns_404_without_checkin` | Atendido |
| Usuário vem só do token; 401 sem token | `test_requires_authentication`, `test_rejects_invalid_token`, `test_rejects_revoked_token` | Atendido |
| Entidade `Recomendacao` com regra e motivo | — | **Não existe** |

**Comentário sugerido para o PR #23 / issue #5:** "A conferência do QA encontrou que `POST /api/checkins` ainda não chama `selecionar_materiais`, não persiste `Recomendacao` e não devolve as recomendações (R06). O `test_ti03...` verifica só 201, nível e tags, por isso passa. O TI-03 e o TI-05 do Quadro 26 ficam como 'não atendido' e 'parcial' até a #19 entrar e a integração ser feita (DEF-01)."

## #6, PR #15: histórico de check-ins

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| Listagem do próprio usuário, mais recente primeiro, `limite` ≤ 30 | `test_service_list_checkins_limits`, `test_api_list_checkins_ordered_desc_and_p1_p5_schema` | Atendido |
| `GET /api/checkins/{id}`: 200 ao dono, 404 a outro usuário | `test_api_get_checkin_by_id_owner_success`, `test_api_get_checkin_by_id_other_user_returns_404` | Atendido |
| TS-03: B não vê dados de A | `test_api_list_checkins_isolation_ts_03` | Atendido, mas sem banco |
| 401 sem token | `test_api_checkins_requires_authentication`, `test_api_checkin_by_id_requires_authentication` | Atendido |
| Testes de integração no PostgreSQL de teste | — | **Lacuna**: os testes de API usam repositório falso e sessão simulada |

**Comentário sugerido:** "Os testes de API do histórico passam, mas substituem o repositório por `FakeCheckinRepository`. A issue pede testes de integração no PostgreSQL de teste cobrindo ordem, limite e isolamento. O isolamento real só é verificado em `test_checkin_repository.py`. Sugestão: repetir o TS-03 com o `client` e as fixtures de banco do `conftest.py` (DEF-05)."

## #17, PRs #32 e #33: regras do check-in e seleção de conteúdo

| Critério da issue | Resultado |
| :-- | :--: |
| TU-05 automatizado, com os dois lados de cada limite, incluindo P1 a P4 sem resposta | Atendido |
| TU-06 automatizado com os casos do Quadro 26 | **Parcial**: 3 testes; faltam ordem, menos recente, sem repetição, máximo de 3, inativos, regra e motivo |
| Toda linha de R-D1 a R-D6 e de R-S1 a R-S6 com ao menos um teste (M1) | **Não atendido**: R-D 6 de 6; R-S 0 de 6 aderentes ([matriz](matriz-regras-testes.md)) |
| Limites em constantes de configuração | Atendido para R-D; `DIAS_BLOQUEIO_ULTIMAS_EXIBICOES` existe em `selecao.py` mas não é usada |
| Sem acesso a banco, rede, relógio ou aleatoriedade | Atendido |
| CI verde | Atendido |

O PR #33 (reparo de TS-01 e TS-04) foi mesclado na mesma branch e está dentro do conjunto aprovado.

**Comentário sugerido:** "O critério de aceite pede toda linha R-S1 a R-S6 com teste. Hoje há 3 testes do TU-06; R-S1, R-S3 (deduplicação) e R-S4 (teto de 3, 2 para N2) não têm teste, e R-S2, R-S5 e R-S6 divergem do Quadro 20 (DEF-02 e DEF-03). Os testes de R-S1, R-S3 e R-S4 não dependem de decisão do PO e podem entrar já."

## #18, PR #30: PHQ-9 e GAD-7

| Critério | Testes | Resultado |
| :-- | :-- | :--: |
| TU-01: soma e entradas inválidas | `test_tu01_*` | Atendido |
| TU-02 e TU-03: faixas nos valores-limite | `test_tu02_*`, `test_tu03_*` | Atendido |
| TU-04: um caso por regra e precedência | `test_tu04_caso1` a `caso8`, `test_tu04_ra1_prevalece_sobre_todas` | Atendido |
| Perfis A a E do Quadro 19 | `test_perfil_a` a `test_perfil_e` | Atendido |

Sem lacunas. Os 69 testes de regras (avaliação e check-in) também foram executados localmente sem banco, com 69 aprovados.

## #19, PR #37: catálogo e seed

| Critério | Resultado |
| :-- | :--: |
| TU-07: esquema válido, slugs únicos, URLs https, domínio permitido, ≥ 1 material ativo por tag | Existe e passa no PR (4 testes; [execução 42728982238](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42728982238)) |
| Seed idempotente, material retirado fica inativo, falha sem arquivo ou com catálogo vazio | 3 testes em `test_seed_materiais.py`, aprovados no PR |
| Conferência dos 7 materiais pelo PO | **Pendente** (PR #37, lista de aceite) |
| Merge na `main` | **Pendente** |

Rodou localmente, sem banco, `test_materiais_tu07.py` e `test_rules_checkin.py` do PR: 10 aprovados. O PR não altera `Recomendacao` (que não existe), logo não destrava sozinho o DEF-01. Ponto do PR para decisão do PO: o único material de HUMOR (`depressao-ms`) tem texto clínico.

## #22: pendências da Sprint 2

Sem PR. Situação por caso do roteiro:

| Caso | Situação |
| :-- | :-- |
| TI-01 | Os testes de `test_register.py` cobrem 201, 409, 422 sem aceite e senha curta, mas não o 422 sem declaração 18+ (a declaração não existe). Não executável como escrito. |
| TI-02 | `test_login_returns_token`, `test_login_rejects_wrong_password`, `test_login_rejects_unknown_user_with_same_message`: atendido. |
| TS-01 | Atendido, com lista pública diferente da prevista (decisão do PO pendente). |
| TS-02 | Parcial: falta o token de usuário excluído (R04, Sprint 5). |
| TS-04 | Parcial: ver DEF-04. |
| TS-05 | Atendido. |

As quatro decisões do PO listadas na #22 (rotas públicas extras, tabela `consents`, limite de tentativas de login e pacotes do backend) continuam abertas; elas têm efeito direto no TS-01 e no registro de defeitos.
