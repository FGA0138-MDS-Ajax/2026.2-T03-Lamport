# Conferência dos PRs da Sprint 4

Tarefa da issue #10: conferir, nos PRs das issues #5, #6, #17, #18, #19 e #22, que cada caso do roteiro previsto para a Sprint 4 existe e roda na CI, e apontar as lacunas. Posição final em 11/11/2026, com os PRs #37 a #44 mesclados.

**Os comentários sugeridos abaixo não foram publicados nos PRs.** As lacunas que seguem abertas estão registradas nas issues `bug` #45, #46 e #47 (ver [Defeitos](defeitos.md)).

## Resumo

| Issue | PR | Casos | Existem e rodam na CI? | Lacuna |
| :--: | :--: | :-- | :--: | :-- |
| #5 | #23 (mesclado) | TI-03, TI-04, TI-05 | Sim, os três | TI-03 e TI-05 não verificam recomendações; funcionalidade ausente (DEF-01) |
| #6 | #15 e #39 (mesclados) | TS-03 (check-ins) | Sim | DEF-05 corrigido no PR #39; parte de avaliações é da Sprint 5 |
| #17 | #32, #33 e #38 (mesclados) | TU-05, TU-06 | Sim | TU-06 sem verificação de inativos e de regra e motivo por item; divergências do Quadro 20, inclusive em R-S1 (DEF-02, DEF-03) |
| #18 | #30 (mesclado) | TU-01 a TU-04 | Sim, sem lacuna | Nenhuma |
| #19 | #37 (mesclado) | TU-07 | Sim, na `main` | Conferência dos 7 materiais pelo PO |
| #22 | #39, #40, #41 e #42 (mesclados) | TI-01, TI-02, TS-01, TS-02, TS-04, TS-05 | Sim, os seis, aprovados | Nenhuma; decisões do PO registradas na v2.3 |

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

**Comentário sugerido para o PR #23 / issue #5:** "A conferência do QA encontrou que `POST /api/checkins` ainda não chama `selecionar_materiais`, não persiste `Recomendacao` e não devolve as recomendações (R06). O `test_ti03...` verifica só 201, nível e tags, por isso passa. O TI-03 e o TI-05 do Quadro 26 ficam como 'não atendido' e 'parcial' até a integração ser feita (DEF-01); o catálogo da #19 já está na `main` (PR #37)."

## #6, PRs #15 e #39: histórico de check-ins

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| Listagem do próprio usuário, mais recente primeiro, `limite` ≤ 30 | `test_service_list_checkins_limits`, `test_api_list_checkins_ordered_desc_and_p1_p5_schema` | Atendido |
| `GET /api/checkins/{id}`: 200 ao dono, 404 a outro usuário | `test_api_get_checkin_by_id_owner_success`, `test_api_get_checkin_by_id_other_user_returns_404` | Atendido |
| TS-03: B não vê dados de A | `test_api_list_checkins_isolation_ts_03` (sem banco); `test_ts03_isolamento.py` (5 testes no banco de teste, PR #39) | Atendido |
| 401 sem token | `test_api_checkins_requires_authentication`, `test_api_checkin_by_id_requires_authentication` | Atendido |
| Testes de integração no PostgreSQL de teste | `test_ts03_isolamento.py` (isolamento pela API, PR #39); `test_checkin_repository.py` (ordem, limite e isolamento no repositório) | Atendido (DEF-05 corrigido); os testes de ordem e limite pela API seguem com repositório falso |

**Comentário sugerido:** nenhum. A sugestão desta conferência, repetir o TS-03 com o `client` e as fixtures de banco do `conftest.py`, foi aplicada no PR #39 (DEF-05 corrigido).

## #17, PRs #32, #33 e #38: regras do check-in e seleção de conteúdo

| Critério da issue | Resultado |
| :-- | :--: |
| TU-05 automatizado, com os dois lados de cada limite, incluindo P1 a P4 sem resposta | Atendido |
| TU-06 automatizado com os casos do Quadro 26 | **Parcial**: 7 testes; verificam ordem (só com as tags do check-in), sem repetição e máximo de 3; faltam ordem com AJUDA_PROFISSIONAL, menos recente, inativos, regra e motivo |
| Toda linha de R-D1 a R-D6 e de R-S1 a R-S6 com ao menos um teste (M1) | **Não atendido**: R-D 6 de 6; R-S 2 de 6 aderentes (R-S3 e R-S4, PR #38; R-S1 tem teste, mas o código diverge) ([matriz](matriz-regras-testes.md)) |
| Limites em constantes de configuração | Atendido para R-D; `DIAS_BLOQUEIO_ULTIMAS_EXIBICOES` existe em `selecao.py` mas não é usada |
| Sem acesso a banco, rede, relógio ou aleatoriedade | Atendido |
| CI verde | Atendido |

O PR #33 (reparo de TS-01 e TS-04) foi mesclado na mesma branch e está dentro do conjunto aprovado. O PR #38 acrescentou os testes de R-S1, R-S3 e R-S4.

**Comentário sugerido:** "O critério de aceite pede toda linha R-S1 a R-S6 com teste aderente ao Quadro 20. Depois do PR #38, R-S3 e R-S4 estão cobertas. R-S1 tem teste, mas `selecao.py` usa a ordem de tags do check-in, sem AJUDA_PROFISSIONAL; a correção não depende do PO. R-S2, R-S5 e R-S6 divergem do Quadro 20 e dependem de decisão do PO (DEF-02). Faltam ainda os testes de inativos, de regra e motivo por item e do teto de 2 para N2 (DEF-03)."

## #18, PR #30: PHQ-9 e GAD-7

| Critério | Testes | Resultado |
| :-- | :-- | :--: |
| TU-01: soma e entradas inválidas | `test_tu01_*` | Atendido |
| TU-02 e TU-03: faixas nos valores-limite | `test_tu02_*`, `test_tu03_*` | Atendido |
| TU-04: um caso por regra e precedência | `test_tu04_caso1` a `caso8`, `test_tu04_ra1_prevalece_sobre_todas` | Atendido |
| Perfis A a E do Quadro 19 | `test_perfil_a` a `test_perfil_e` | Atendido |

Sem lacunas. Os 73 testes de regras (avaliação e check-in) também foram executados localmente sem banco, com 73 aprovados.

## #19, PR #37: catálogo e seed

| Critério | Resultado |
| :-- | :--: |
| TU-07: esquema válido, slugs únicos, URLs https, domínio permitido, ≥ 1 material ativo por tag | Atendido (4 testes; CI da `main`, [execução 43118733055](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/43118733055)) |
| Seed idempotente, material retirado fica inativo, falha sem arquivo ou com catálogo vazio | Atendido (4 testes em `test_seed_materiais.py`) |
| Conferência dos 7 materiais pelo PO | **Pendente** (lista de aceite do PR #37) |
| Merge | Concluído |

O PR não cria `Recomendacao`, logo não destrava sozinho o DEF-01. Ponto para decisão do PO: o único material de HUMOR (`depressao-ms`) tem texto clínico.

## #22: pendências da Sprint 2

PRs #39 (alinhamento e testes), #40 (decisões do PO na Visão e Arquitetura v2.3), #41 (campos em português) e #42 (ajuste do job `demo`). Situação por caso do roteiro:

| Caso | Situação |
| :-- | :-- |
| TI-01 | Aprovado: 201, 409, 422 sem aceite dos termos, 422 sem declaração 18+ e 422 com senha curta (`test_register.py`). |
| TI-02 | Aprovado: login, senha errada e e-mail inexistente com a mesma mensagem, e limite de tentativas (429). |
| TS-01 | Aprovado, com a lista pública da v2.3 (`/api/auth/cadastro`, `/api/auth/login`, `/api/terms`, `/api/health`). |
| TS-02 | Aprovado: expirado, outra chave, malformado e usuário excluído, todos com 401. |
| TS-04 | Aprovado: `GET /api/me` devolve só `id`, `email` e `criado_em`. |
| TS-05 | Aprovado. |

Duas observações do QA: (1) o PR #41 renomeou os campos de entrada e deixou o job `demo` da CI com o campo antigo (`password`); a execução da `developer` falhou com 422 e o PR #42 corrigiu; (2) os testes de Ajuda e Check-in que vieram da `main` ainda simulavam `/api/users/me`, ajustados no PR #43 ao integrar `main` e `developer`. As decisões do PO sobre as divergências estão registradas na [Visão e Arquitetura v2.3](../historico-versoes.md); as de pacotes do backend e da entidade Consentimento foram resolvidas atualizando o documento ao código.
