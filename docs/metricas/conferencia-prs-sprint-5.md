# Conferência dos PRs da Sprint 5

Tarefa da issue #62: conferir cada PR da sprint contra o resultado esperado do Quadro 26 da Visão v2.7 e os critérios de aceite da issue. Posição em 25/11/2026, às 22h55, com os PRs #66 a #78 mesclados na `developer` e levados à `main` pelo PR #80 (`main` no commit `22bf6a4`), e o #65 na `docs`. Evidência dos casos automatizados: [execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093) da CI na `main`.

## Resumo

| Issue | PR | Casos | Existem e rodam na CI? | Lacuna |
| :--: | :--: | :-- | :--: | :-- |
| #46, #47 | #66 (mesclado) | TU-06 | Sim | Nenhuma no código. Mesclado sem nova aprovação depois do pedido de mudanças. |
| #45 | #67 (mesclado) | TI-03, TI-05 | Sim | Nenhuma no código. Revisão do PO só com comentário, sem aprovação. |
| #51 | #68 (mesclado) | Repositório e cascata | Sim | `downgrade` sem teste automatizado (verificado à mão pelo QA). Aprovado pelo PO antes do merge. |
| #54 | #69 (mesclado) | TI-06 | Sim | Nenhuma. Aprovado pelo PO antes do merge. |
| #55 | #70 (mesclado) | TS-03 (avaliações) | Sim | Nenhuma no código. Mesclado sem revisão registrada. |
| #56 | #71 (mesclado) | TSI-01 | Sim (vitest) | Nenhuma no código. Mesclado sem revisão registrada. |
| #53 | #72 (mesclado) | — (prepara TSI-03) | Sim (vitest) | Arquivo de mocks sem uso. Mesclado sem revisão registrada. |
| #52 | #65 (mesclado, `docs`) | — | n/a | Marcadores de conflito no `mkdocs.yml` (DEF-09), corrigidos por push direto na `docs`. Mesclado sem revisão registrada. |
| #60 | #73 (mesclado) | TI-07 | Sim | Nenhuma. Aprovado pelo QA antes do merge. |
| #58 | #75 (mesclado) | TSI-03 (resultado) | Sim (vitest) | Nenhuma. Aprovado pelo QA antes do merge. |
| #61 | #74 (mesclado) | TSI-05 | Sim (vitest) | Nenhuma no código. Mesclado sem revisão registrada. |
| #57 | #77 (mesclado) | TSI-03 | Sim (vitest) | Nenhuma. Aprovado pelo QA antes do merge. |
| #59 | #76 (mesclado) | TSI-03 (histórico) | Sim (vitest) | Nenhuma no código. Mesclado sem revisão registrada. |
| — (DEF-10) | #78 (mesclado) | Histórico vazio | Sim (vitest), sem teste novo | Corrige o botão "Fazer o primeiro check-in". Aprovado pelo QA antes do merge. |

## #46 e #47, PR #66: seleção de conteúdo conforme o Quadro 20

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| R-S1: ordem AJUDA_PROFISSIONAL → … → BEM_ESTAR, só materiais ativos | `test_tu06_rs1_ordem_prioridade_com_ajuda_profissional`, `test_tu06_rs1_material_inativo_nunca_sugerido` | Atendido |
| R-S2: nunca recomendado primeiro, depois o mais antigo, empate pelo menor id | `test_tu06_rs2_nunca_recomendado_depois_mais_antigo_e_desempate_menor_id` | Atendido |
| R-S3: sem repetição | `test_tu06_rs3_material_com_duas_tags_aparece_uma_vez` | Atendido |
| R-S4: no máximo 3, 2 para N2, descarte por prioridade | `test_tu06_rs4_limite_tres_padrao_e_limite_dois_n2` | Atendido |
| R-S5: regra de origem e motivo por item (check-in e avaliação) | `test_tu06_rs5_checkin_preserva_regra_e_motivo_quadro_16`, `test_tu06_rs5_avaliacao_preserva_regra_e_motivo_quadro_18` | Atendido |
| R-S6: sem material, lista vazia, sem fallback | `test_tu06_rs6_sem_material_disponivel_retorna_vazio_sem_fallback` | Atendido |
| Catálogo de teste com 2 materiais por tag, 1 inativo (Quadro 26) | fixture `catalogo_tu06` | Atendido |
| Contrato coerente com o Quadro 5 da Arquitetura | `selecionar_materiais(tags, catalogo, ultimas_exibicoes, limite=3)` | Atendido |
| M1 = 100% | [matriz](matriz-regras-testes.md) | Atendido |

**Observação para o PO (não é defeito):** a implementação escolhe **um material por tag**, como o PO pediu na revisão do PR (R-S2: "escolher o material" entre os candidatos de uma tag). Uma consequência: no N2, que só tem a tag AJUDA_PROFISSIONAL, sai sempre 1 material, e o teto de 2 do R-S4 e do Quadro 18 ("até 2 materiais") nunca é atingido, embora o catálogo tenha 4 materiais ativos com essa tag. "Até 2" admite 1, então o comportamento está dentro do documento. Se a intenção for mostrar 2 no N2, a mudança começa pelo Quadro 20, em nova versão da Visão.

**Processo:** a revisão do PO pediu mudanças (CHANGES_REQUESTED, 23/11) e o ajuste foi feito no commit `f13f1e5` (24/11), mas o PR foi mesclado sem nova aprovação registrada no GitHub.

## #45, PR #67: recomendações no check-in

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| TI-03: 201, tags [ANSIEDADE, SONO], 2 recomendações persistidas com R-D3 e R-D4 | `test_ti03_create_checkin_returns_201_with_nivel_tags_and_persists_recomendacoes` (confere resposta e banco) | Atendido |
| TI-05: CRISE, lista vazia, nenhuma linha em `recomendacoes` | `test_ti05_risk_answer_returns_crise_without_tags_or_recomendacoes` | Atendido |
| `GET /api/checkins/hoje` devolve as mesmas recomendações do POST (DP-2) | `test_today_returns_checkin_of_the_day_with_same_recomendacoes_as_post` | Atendido |
| R-S2 com o histórico real do banco | `test_rs2_checkin_uses_ultimas_exibicoes_from_database` | Atendido |
| TI-04, TS-01 e TS-04 continuam aprovados | CI | Atendido |
| Integração no PostgreSQL de teste conferindo o banco | idem | Atendido |

Uma execução da CI do PR falhou no teste de R-S2 ([44953808003](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/44953808003)) e foi corrigida no próprio PR (commit `2d7fcb7`). No ambiente de demonstração, o `POST /api/checkins` devolveu as recomendações esperadas, e com a tela da #71 o TSI-01 foi aprovado (ver [ciclo 1](sprint-5.md#roteiro-de-sistema-ciclo-1)).

## #51, PR #68: modelo e migração da Avaliacao

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| `alembic upgrade head` e `downgrade` | `test_migrations_match_models` (modelos × migrações); `downgrade 0005`, `downgrade base` e `upgrade head` executados pelo QA no banco do ambiente de demonstração em 25/11, sem erro | Atendido (o `downgrade` não tem teste automatizado) |
| Gravação e busca por id | `test_add_and_get_by_id_for_user` | Atendido |
| Busca por id de outro usuário devolve nada | `test_get_by_id_other_user_returns_none` | Atendido |
| Listagem só do próprio usuário, mais recente primeiro | `test_list_by_user_newest_first_and_only_own_records` | Atendido |
| Exclusão do usuário remove avaliações e recomendações | `test_cascade_delete_user_removes_avaliacoes`, `test_recomendacao_linked_to_avaliacao_and_cascade_delete` | Atendido |

## #54, PR #69: `POST /api/avaliacoes`

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| TI-06: perfis A a E com escores, faixas, nível e tags do Quadro 19; recomendações persistidas conforme R-S; perfil C com no máximo 2, de AJUDA_PROFISSIONAL; perfil D sem nenhuma | `test_ti06_perfis_a_a_e_quadro_19_persistem_avaliacao_e_recomendacoes` | Atendido |
| Regra do nível (R-A2 a R-A4) e motivo do Quadro 18 em cada recomendação (DP-1) | idem | Atendido |
| Entradas inválidas (tamanho, valor 4 ou −1) → 422, sem gravar nada | `test_invalid_avaliacao_payload_returns_422` (17 casos) | Atendido |
| TS-01 e TS-04 com a rota nova | CI | Atendido |
| Conteúdo da avaliação fora dos logs | `test_avaliacao_content_is_not_logged` | Atendido |

No ambiente de demonstração, o perfil B pela API devolveu 10/5, moderada/leve, N1 e 2 materiais ([resposta](evidencias/sprint-5/tsi03-api-perfil-b.json)). Falta a tela para o TSI-03.

## #55, PR #70: `GET /api/avaliacoes` e `/{id}`

| Critério da issue | Teste | Resultado |
| :-- | :-- | :--: |
| TS-03: B recebe 404 em `GET /api/avaliacoes/{id de A}`; listagem de B sem dados de A | `test_ts03_user_b_gets_404_for_avaliacao_of_user_a`, `test_ts03_listing_of_user_b_does_not_contain_data_of_user_a`, `test_ts03_404_for_other_user_matches_404_for_unknown_id`, `test_ts03_each_user_reads_only_own_avaliacao_by_id` | Atendido |
| Testes com o `client` e o banco de teste, sem repositório falso | `test_avaliacoes_get.py` usa o `client` e as fixtures do `conftest.py` | Atendido |
| Saída do `/{id}` igual à do POST (DP-3), sem gerar recomendações de novo | `test_detail_returns_same_body_as_post`, `test_detail_does_not_regenerate_recommendations` | Atendido |
| Listagem sem as respostas brutas, mais recente primeiro | `test_list_does_not_expose_raw_answers`, `test_list_returns_all_avaliacoes_most_recent_first` | Atendido |
| TS-01 e TS-04 continuam aprovados | CI | Atendido |

**Processo:** o PR foi aberto pelo QA e mesclado pelo PO sem revisão registrada no GitHub. Como o autor é também quem confere a sprint, esta conferência não substitui a revisão de outro integrante.

## #56, PR #71: materiais do dia no check-in

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Materiais e motivos exibidos após o envio | `mostra os materiais e os motivos após o envio` (`DailyCheckin.test.tsx`); TSI-01 no navegador | Atendido |
| Resultado do dia ao reabrir o check-in (DP-2) | `mostra o resultado gravado do dia ao reabrir o check-in`; `mostra o resultado do dia quando o envio responde 409` | Atendido |
| Links com `target="_blank"` e `rel="noopener noreferrer"` | asserções em `DailyCheckin.test.tsx`; no navegador, o link abriu em nova aba a página do gov.br | Atendido |
| P5 = Sim abre a Tela de Ajuda | `opens the help screen after saving the check-in`, `opens the help screen, without materials, when reopening a crisis check-in`, `still opens the help screen when saving fails`; TSI-02 no navegador | Atendido |
| ESLint e testes do frontend verdes na CI | job `frontend` da [execução 45713485445](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45713485445): ESLint/Prettier, 54 testes do vitest e build aprovados | Atendido |

A tela também trata a lista vazia (R-S6: "Não encontramos materiais para hoje"), com teste próprio, e deixa claro que o check-in "não é um teste de saúde".

**Processo:** o PR foi aberto pelo PO e mesclado pelo QA, sem revisão registrada no GitHub.

## #52, PR #65: vocabulário da avaliação e protótipo (branch `docs`)

| Critério da issue | Verificação | Resultado |
| :-- | :-- | :--: |
| Textos conferidos com a fonte oficial e validados pelo PO | Página `vocabulario-avaliacao.md` cita a fonte (phqscreeners.com, acesso em 16/11/2026); o PR foi mesclado pelo PO, sem revisão registrada | Atendido pelo merge do PO |
| Protótipo linkado na issue e revisado pelo PO | Links do Figma na página (arquivo e protótipo navegável), não na issue | Atendido em parte |
| Página publicada por PR na branch `docs` | O merge deixou marcadores de conflito no `mkdocs.yml` e o deploy falhou ([execução 45713457088](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45713457088), DEF-09). O commit `eedab0a` corrigiu e a [execução 45716938818](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45716938818) publicou o site | Atendido depois da correção |

## #53, PR #72: cliente de API das avaliações

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Testes do cliente no padrão de `checkins.test.ts` | `avaliacoes.test.ts` (8 testes): criar com PHQ-9 e GAD-7, 422, listar, lista vazia, 401, buscar por id com os campos do POST (DP-3), 404 e erro de rede | Atendido |
| ESLint e testes do frontend verdes na CI | job `frontend` da [execução 45717806353](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45717806353): ESLint/Prettier, 62 testes do vitest e build aprovados | Atendido |

Os três métodos (`POST /api/avaliacoes`, `GET /api/avaliacoes` e `GET /api/avaliacoes/{id}`) chamam a API real; os tipos seguem o Quadro 6 da Arquitetura e reusam `Recomendacao` do check-in.

**Observações:** o PR acrescenta `frontend/src/mocks/avaliacoes.ts`, que nenhum arquivo importa; pode ser removido ou usado pelas telas da #57 e da #58. O PR não tem "Closes #53" (a issue foi fechada à mão) e foi mesclado pelo QA sem revisão registrada.

## #60, PR #73: `DELETE /api/me`

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| TI-07: usuário com check-ins, avaliações e recomendações → 204; zero linhas do usuário em todas as tabelas; token antigo → 401 | `test_ti07_delete_only_the_authenticated_account_and_its_data`: confere `users`, `consents`, `checkins`, `avaliacoes`, `recomendacoes`, `revoked_tokens` e `login_attempts`, que os dados do outro usuário e os materiais continuam, e 401 para token antigo, token revogado e novo login | Atendido |
| TS-01 (rota protegida), TS-02 e TS-04 aprovados | TS-01 percorre o contrato OpenAPI e já inclui `DELETE /api/me`; o caso "usuário excluído" do TS-02 passa a usar a exclusão real | Atendido |
| Testes no PostgreSQL de teste; CI verde | `test_delete_account.py` com o `client` e o banco de teste; [execução 45721206219](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45721206219) | Atendido |

**Verificação do QA no ambiente de demonstração (25/11):** conta com check-in e avaliação → `DELETE /api/me` 204 sem corpo; `GET /api/me` com o token antigo e novo login → 401; nenhuma linha restante em `users`, `checkins`, `avaliacoes`, `recomendacoes` e `consents`; os 7 materiais intactos. A migração 0007 (dono do token revogado, com `ON DELETE CASCADE`) fez `downgrade` e `upgrade` sem erro.

**Observações:** revogações de token anteriores à migração 0007 ficam com `user_id` nulo e não são apagadas com a conta; guardam só um identificador aleatório e a validade, sem dado pessoal, e expiram com o token. O PR não tem "Closes #60" (a issue foi fechada à mão). Foi aprovado pelo QA antes do merge.

## #58, PR #75: tela de resultado da avaliação

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Perfil B: escores 10/5, faixas Moderada/Leve, orientação de procurar a UBS, aviso "não é diagnóstico" e 2 materiais (TSI-03) | `mostra o resultado do perfil B carregado por GET /api/avaliacoes/{id} (TSI-03)`; no navegador, com a avaliação criada pela API, a tela mostra todos os itens ([captura](evidencias/sprint-5/tsi03-06-resultado.png)) | Atendido |
| Avaliação de outro usuário (404) mostra mensagem de não encontrado | `mostra "não encontrada" quando a API responde 404 (avaliação de outro usuário)`; no navegador, "Avaliação não encontrada" ([captura](evidencias/sprint-5/tsi03-07-avaliacao-de-outro-usuario.png)) | Atendido |
| ESLint e testes do frontend verdes na CI | job `frontend` da [execução 45728060182](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45728060182): 72 testes | Atendido |

Também cobertos: id inválido (422), erro genérico da API, resultado recebido pela navegação logo após o envio (sem nova chamada à API) e nível crise, que esconde os materiais e leva à Tela de Ajuda Imediata. Os motivos do Quadro 18 aparecem abertos por padrão em "Por que estou vendo isto?". O PR removeu o arquivo de mocks sem uso que a #72 tinha deixado.

**Processo:** aprovado pelo QA antes do merge.

## #61, PR #74: excluir conta com confirmação

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Cancelar não exclui; confirmar chama a rota, limpa a sessão e redireciona | `does not delete the account when the user cancels`, `calls DELETE /api/me, clears the session and redirects on confirmation` (`ExcluirConta.test.tsx`); também o aviso de que todos os dados serão apagados e o erro mantendo a sessão | Atendido |
| Depois da exclusão, o login com as mesmas credenciais falha (TSI-05) | TSI-05 no navegador, execução 3: `DELETE /api/me` 204, token removido da sessão e novo login com "E-mail ou senha incorretos." ([captura](evidencias/sprint-5/tsi05-08-login-falha.png)) | Atendido |
| ESLint e testes do frontend verdes na CI | [execução 45728060182](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45728060182) | Atendido |

**Observação:** a tarefa diz "voltar à página inicial". O componente navega para `/`, mas como a página inicial exige login, o usuário cai na tela de login, que é a página inicial de quem não tem sessão. O comportamento atende ao R04; se o PO quiser outra tela, o ajuste é de uma linha.

**Processo:** o PR foi aberto pelo QA e mesclado pelo PO, sem revisão registrada no GitHub.

## #57, PR #77: tela da avaliação quinzenal

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Envio bloqueado com item sem resposta; item 9 ≥ 1 abre a Tela de Ajuda; envio válido leva ao resultado | `AvaliacaoPage.test.tsx`; no navegador (execução 4): envio vazio bloqueado com a lista das perguntas que faltam, perfil D levando à Tela de Ajuda sem materiais e perfil B levando ao resultado | Atendido |
| Botão "Preciso de ajuda agora" visível (R11) | Visível na tela da avaliação ([captura](evidencias/sprint-5/tsi03-05-avaliacao-perfil-b.png)) | Atendido |
| ESLint e testes do frontend verdes na CI | job `frontend` da [execução 45735248030](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45735248030): 85 testes | Atendido |

Os 16 itens usam os textos oficiais da #52, com a escala de 4 opções; a tela informa que o recomendado é responder a cada duas semanas e entra no menu ("Avaliação") e na página inicial ("Avaliação quinzenal").

**Processo:** aprovado pelo QA antes do merge.

## #59, PR #76: avaliações no histórico

| Critério da issue | Teste ou verificação | Resultado |
| :-- | :-- | :--: |
| Testes com lista vazia, com avaliações e com erro da API | `HistoryPage.test.tsx` | Atendido |
| Check-ins continuam exibidos como antes | Testes da lista de check-ins mantidos; no navegador, o TSI-01 mostra o check-in do dia como antes ([captura](evidencias/sprint-5/tsi01-06-historico.png)) | Atendido |
| ESLint e testes do frontend verdes na CI | [execução 45735248030](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45735248030) | Atendido |

Cada avaliação mostra data, escores, faixas e nível e abre o resultado da #58 ([captura](evidencias/sprint-5/tsi03-07-historico.png)), como pede a tarefa que dependia da #58. Os rótulos de faixa e nível foram extraídos para `constants/avaliacao.ts` e passaram a ser usados também pela tela de resultado.

**Processo:** o PR foi aberto pelo QA e mesclado pelo PO, sem revisão registrada no GitHub.

## PR #78: botão "Fazer o primeiro check-in" do histórico (DEF-10)

Correção feita pela equipe, sem issue. O botão do histórico vazio existia desde o PR #29 (Sprint 4) sem ação ao clicar; o PR #78 passa a levar à tela do check-in.

| Verificação | Resultado |
| :-- | :--: |
| No navegador (execução 5), "Fazer o primeiro check-in" abre a tela do check-in ([captura](evidencias/sprint-5/historico-01-primeiro-checkin.png)) | Atendido |
| CI verde ([execução 45737073884](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45737073884)); a primeira execução do PR falhou na formatação (Prettier) e foi corrigida no próprio PR | Atendido |
| Teste automatizado do botão | **Não há**: `HistoryPage.test.tsx` não verifica o clique |

**Observações:** (1) o defeito passou pelas revisões das Sprints 4 e 5 porque nenhum teste clicava no botão; um teste de clique evita que volte. (2) O botão perdeu a classe `history-empty-button`, que dava um espaçamento de 0,25rem acima; o efeito visual é mínimo. (3) A navegação usa `/DailyCheckin`, com maiúsculas, enquanto a rota é `dailycheckin`; funciona porque o roteador não diferencia maiúsculas, como já acontecia na página inicial.

**Processo:** aprovado pelo QA antes do merge.

## PR #80: `developer` → `main`

Aberto e mesclado pelo PO em 25/11/2026, às 22h50, sem revisão registrada. Leva à `main` todas as entregas da sprint (PRs #66 a #78). Depois do merge, a `main` (`22bf6a4`) tem conteúdo idêntico ao da `developer` (`0dca653`), e a CI da `main` passou: [execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093), com 298 testes no backend, 85 no frontend e o job `demo`. Com isso, a evidência do roteiro deixa de depender da `developer`, e a execução 5 do ciclo 1, feita no mesmo conteúdo, vale para a `main`.

## Issues sem PR na sprint

Só a #63, do PO, que não tem código: faltam a retrospectiva da Sprint 4, a conferência dos 7 materiais e o Quadro 21, o quadro da sprint no GitHub Projects e a revisão da Sprint 5.
