# Sprint 5: Pendências da Sprint 4, avaliação e histórico (12/11 a 25/11/2026)

**Posição em 25/11/2026, às 22h55** (horário de Brasília) (dia 14 de 14). Acompanha a issue #62. Base: [Visão v2.7](../visao-produto-projeto.md), [Arquitetura v2.5](../arquitetura.md) e o [Planejamento da Sprint 5](../sprints/sprint-5.md).

!!! info "Entregas na `main` pelo PR #80"
    Os PRs #66 a #78 foram mesclados na `developer` e levados à `main` pelo PR #80, em 25/11/2026, às 22h50. A `main` ficou no commit `22bf6a4`, com conteúdo idêntico ao da `developer` no commit `0dca653`. A evidência dos casos automatizados é a [execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093) da CI na `main`. O ciclo 1 do roteiro de sistema foi executado com a `developer`; a execução final (5) usou o commit `0dca653`, de conteúdo idêntico ao da `main`, e por isso vale para a `main`, como pede o Quadro 25.

## Métricas

| Métrica | Valor | Esperado | Observação |
| :-- | :--: | :--: | :-- |
| M1. Cobertura das tabelas de regras | **100%** (16 de 16) | 100% | R-S1 a R-S6 passam a aderir ao Quadro 20 (PR #66). Ver [matriz](matriz-regras-testes.md). |
| M2. Aprovação dos testes automatizados | **100%** (298 de 298 no backend; 85 de 85 no frontend) | 100% na `main` | [Execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093), `main` no commit `22bf6a4` (PR #80); jobs `backend`, `frontend` (com ESLint) e `demo` aprovados. Na `main` (`886e00b`) segue o valor da Sprint 4 (210 de 210). |
| M3. Testes de segurança aprovados | **100%** (5 de 5) | 100% | TS-03 completo com a parte de avaliações no banco de teste (PR #70). Nenhum teste reprovado. |
| M4. Conclusão da sprint | **93,8%** (15 de 16), igual pelo estado das issues e pelos critérios de aceite | ≥ 80% (referência) | Acima da referência. Só falta a #63, do PO; com ela, 100%. A #62 é contada como concluída, pois é fechada pelo PR com estes registros. Ver abaixo. |
| M5. Defeitos abertos por severidade | **0** issues `bug` abertas; **5** defeitos novos (0 críticos, 2 altos, 2 médios, 1 baixo), dos quais só 1 segue aberto: DEF-08 (médio, issue a abrir). DEF-06 corrigido no PR #71; DEF-07 corrigido nos PRs #75 e #77; DEF-10 corrigido no PR #78; DEF-09 corrigido pelo commit `eedab0a` na `docs`. Os 3 defeitos da Sprint 4 (#45 a #47) estão corrigidos | 0 críticos | Ver [Defeitos](defeitos.md). |

**Critérios de aceite da issue #62:**

| Critério | Situação |
| :-- | :-- |
| M1 a M5 registradas, com M1 e M3 a 100% ou a justificativa | **Atendido:** M1 = 100% e M3 = 100%. |
| TSI-01 a TSI-04 executados e com evidência | **Atendido:** os quatro foram executados em 25/11/2026, em cinco execuções, com capturas de tela ([evidências](#roteiro-de-sistema-ciclo-1)), e estão **aprovados** na execução final. O TSI-05, da Sprint 6, também foi executado e aprovado. |
| Nenhum defeito crítico aberto no fim da sprint | **Atendido:** nenhum dos defeitos é crítico. A jornada de risco (TSI-02) e a Ajuda Imediata sem login (TSI-04) funcionam, nenhum teste de segurança falha e as regras em uso encaminham corretamente (TU-06, TI-03, TI-05, TI-06, TSI-01 e TSI-03 aprovados). |

## Roteiro de testes da Sprint 5

Casos previstos para a sprint (Visão, Quadro 26) e os que voltaram por pendência da Sprint 4. Evidência dos automatizados: [execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093) da CI na `main`.

### Testes unitários e de integração

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TU-06 | **Aprovado** | `test_tu06_*` em `test_rules_checkin.py` (9 testes: R-S1 com AJUDA_PROFISSIONAL e inativos; R-S2 nunca recomendado, mais antigo e desempate; um material por tag; R-S3; R-S4 com teto 3 e teto 2 para N2; R-S5 do check-in e da avaliação; R-S6 sem fallback) | PR #32, #38 e #66 | 3 | O catálogo de teste tem 2 materiais por tag, 1 inativo, como pede o Quadro 26. DEF-02 e DEF-03 corrigidos. |
| TI-03 | **Aprovado** | `test_ti03_create_checkin_returns_201_with_nivel_tags_and_persists_recomendacoes` | PR #23 e #67 | 3 | Confere 201, tags [ANSIEDADE, SONO] e 2 recomendações na resposta e no banco, com regras R-D3 e R-D4, motivo do Quadro 16, material ativo e da tag. DEF-01 corrigido. |
| TI-05 | **Aprovado** | `test_ti05_risk_answer_returns_crise_without_tags_or_recomendacoes` | PR #23 e #67 | 3 | Confere CRISE, lista vazia na resposta e nenhuma linha em `recomendacoes`. |
| TI-06 | **Aprovado** | `test_ti06_perfis_a_a_e_quadro_19_persistem_avaliacao_e_recomendacoes` (parametrizado com os perfis A a E) | — | 1 | Escores, faixas, nível e orientação na resposta e no banco; recomendações com a regra do nível (R-A2 a R-A4) e o motivo do Quadro 18; perfil D sem recomendações. PR #69. |
| TI-07 | **Aprovado** | `test_ti07_delete_only_the_authenticated_account_and_its_data` (`test_delete_account.py`) | — | 1 | Usuários A e B com check-in, avaliação, recomendações, consentimentos, token revogado e tentativa de login; A exclui a conta → 204 sem corpo; zero linhas de A em `users`, `consents`, `checkins`, `avaliacoes`, `recomendacoes`, `revoked_tokens` e `login_attempts`; dados de B e materiais intactos; token antigo, token revogado e novo login de A → 401. PR #73. Repetido pelo QA no ambiente de demonstração em 25/11 (204, token antigo e login → 401, nenhuma linha restante). |

O R-S2 também é verificado na integração: `test_rs2_checkin_uses_ultimas_exibicoes_from_database` e `test_rs2_avaliacao_rotaciona_materiais_com_ultimas_exibicoes`. A única execução reprovada da CI na sprint foi nesse teste, no PR #67, corrigida no próprio PR.

### Testes de segurança

| ID | Status | Testes que o cobrem | Reparos | Ciclos | Observação |
| :-- | :--: | :-- | :--: | :--: | :-- |
| TS-01 | Aprovado | `test_ts01_*` | PR #33 e #39 | 3 | As rotas novas de avaliações e o `DELETE /api/me` entram na verificação automaticamente. Segue a observação da Sprint 4: o teste percorre o contrato OpenAPI, e não `app.routes`. |
| TS-02 | Aprovado | `test_auth.py`, `test_security.py`, `test_delete_account.py` | PR #39 e #73 | 2 | O caso do usuário excluído passa a usar a exclusão real (`DELETE /api/me`, PR #73), no lugar da remoção direta no banco. |
| TS-03 | **Aprovado** | `test_ts03_isolamento.py` (check-ins); `test_ts03_*` em `test_avaliacoes_get.py` (4 testes de avaliações com o `client` e o banco de teste); `test_get_by_id_other_user_returns_none` em `test_avaliacao_repository.py` | PR #39 e #70 | 3 | B recebe 404 em `GET /api/avaliacoes/{id de A}`, igual ao de um id inexistente, e a listagem de B não traz avaliações de A. |
| TS-04 | Aprovado | `test_ts04_*` e o cliente de teste que varre toda resposta JSON | PR #33 e #39 | 3 | A varredura passa a incluir as respostas de avaliações. `test_list_does_not_expose_raw_answers` confere também que a listagem não devolve as respostas brutas. |
| TS-05 | Aprovado | `test_register_stores_only_password_hash` | — | 1 | Sem mudança. |

Os demais casos automatizados (TU-01 a TU-05, TU-07, TI-01, TI-02 e TI-04) continuam aprovados na mesma execução.

<a id="roteiro-de-sistema-ciclo-1"></a>
### Roteiro de sistema, ciclo 1

**Ambiente:** demonstração (Quadro 25) com Docker Compose, banco novo, catálogo real carregado por `python -m app.seed_materiais` (7 materiais) e usuários criados pelo próprio roteiro. **Navegador:** Google Chrome, conduzido pelo script [`roteiro-tsi.mjs`](evidencias/sprint-5/roteiro-tsi.mjs), que repete os passos do Quadro 26 e salva as capturas; o QA conferiu cada captura antes de registrar o status.

| Execução | Data | Commit da `developer` | Registro |
| :--: | :-- | :-- | :-- |
| 1 | 25/11/2026, 19h20 | `e502f3c` (até o PR #70) | [`execucao-1.txt`](evidencias/sprint-5/execucao-1.txt) |
| 2 | 25/11/2026, 19h32 | `9825b79` (com o PR #71) | [`execucao-2.txt`](evidencias/sprint-5/execucao-2.txt) |
| 3 | 25/11/2026, 21h23 | `5231832` (com os PRs #72 a #75) | [`execucao-3.txt`](evidencias/sprint-5/execucao-3.txt) |
| 4 | 25/11/2026, 22h24 | `9ce6609` (com os PRs #76 e #77) | [`execucao-4.txt`](evidencias/sprint-5/execucao-4.txt) |
| 5 | 25/11/2026, 22h42 | `0dca653` (com o PR #78; mesmo conteúdo da `main` `22bf6a4`) | [`execucao-5.txt`](evidencias/sprint-5/execucao-5.txt) |

Os casos TSI-01 a TSI-04 foram executados nas cinco vezes; o TSI-05 (previsto para a Sprint 6) foi executado nas execuções 3 a 5, por ser o critério de aceite da #61. A execução 5 repetiu tudo depois do PR #78 (DEF-10), que mexeu no histórico. A tabela traz o resultado da execução 5, a final da sprint.

| ID | Status | Resultado obtido | Evidência | Reparos | Execuções |
| :-- | :--: | :-- | :-- | :--: | :--: |
| TSI-01 | **Aprovado** | Cadastro, login e check-in (P1 = Ruim, demais favoráveis). A tela mostra "Conteúdos para hoje" com 1 material de HUMOR ("Depressão – Saúde de A a Z", Ministério da Saúde) e, em "Por que estou vendo isto?", o motivo de R-D2. "Abrir no site oficial" abre em nova aba a página do gov.br. O histórico mostra o check-in do dia com o tema Humor, e agora também a seção de avaliações. Na execução 1, a tela voltava ao início sem mostrar o material ([captura](evidencias/sprint-5/tsi01-execucao1-apos-checkin.png), DEF-06). | [check-in](evidencias/sprint-5/tsi01-04-checkin-preenchido.png), [materiais](evidencias/sprint-5/tsi01-05-apos-checkin.png), [motivo](evidencias/sprint-5/tsi01-05b-motivo-aberto.png), [fonte oficial](evidencias/sprint-5/tsi01-05c-fonte-oficial.png), [histórico](evidencias/sprint-5/tsi01-06-historico.png) | PR #71 | 5 |
| TSI-02 | **Aprovado** | Com P5 = Sim, a tela vai para a Ajuda Imediata com CVV 188 e SAMU 192. A API devolve nível CRISE e lista de recomendações vazia; nenhum material é exibido. | [check-in](evidencias/sprint-5/tsi02-04-checkin-preenchido.png), [Tela de Ajuda](evidencias/sprint-5/tsi02-05-apos-checkin.png) | — | 5 |
| TSI-03 | **Aprovado** | Pela página inicial, "Avaliação quinzenal" abre a tela com os 16 itens (PHQ-9 e GAD-7) e o botão "Preciso de ajuda agora" visível. Enviar sem respostas é bloqueado, com a lista das perguntas que faltam. Com o perfil B marcado na tela, o envio leva ao resultado: escores 10 de 27 e 5 de 21, faixas Moderada e Leve, orientação "Procurar a UBS", aviso "Este resultado não é um diagnóstico" e 2 materiais com link e motivo do Quadro 18. O histórico lista a avaliação (PHQ-9 10 · Moderada, GAD-7 5 · Leve, nível Procurar a UBS) e, ao clicar, abre o mesmo resultado; a avaliação de outro usuário mostra "Avaliação não encontrada". Nas execuções 1 e 2 não havia telas, e na 3 só a de resultado (DEF-07). | [avaliação vazia](evidencias/sprint-5/tsi03-04-avaliacao-vazia.png), [perfil B](evidencias/sprint-5/tsi03-05-avaliacao-perfil-b.png), [resultado](evidencias/sprint-5/tsi03-06-resultado.png), [histórico](evidencias/sprint-5/tsi03-07-historico.png), [resultado pelo histórico](evidencias/sprint-5/tsi03-08-resultado-pelo-historico.png), [outro usuário](evidencias/sprint-5/tsi03-07-avaliacao-de-outro-usuario.png) | PR #75 e #77 | 5 |
| TSI-04 | **Aprovado** | Sem sessão, o botão "Preciso de ajuda agora" aparece na tela de login; ao clicar, abre a Tela de Ajuda com CVV 188 e SAMU 192. | [login](evidencias/sprint-5/tsi04-01-login-sem-sessao.png), [Tela de Ajuda](evidencias/sprint-5/tsi04-02-tela-ajuda.png) | — | 5 |
| TSI-05 | **Aprovado** (antecipado da Sprint 6) | Usuário com check-in. Na página inicial, "Excluir conta" abre a confirmação "Excluir sua conta?", que avisa que check-ins, avaliações e recomendações serão apagados sem recuperação. "Cancelar" fecha a confirmação e a sessão continua válida (`GET /api/me` → 200). "Excluir definitivamente" chama `DELETE /api/me` (204), apaga o token da sessão e leva à tela de login. O login com as mesmas credenciais falha com "E-mail ou senha incorretos." | [confirmação](evidencias/sprint-5/tsi05-06-confirmacao.png), [após excluir](evidencias/sprint-5/tsi05-07-apos-excluir.png), [login falha](evidencias/sprint-5/tsi05-08-login-falha.png) | — | 3 |

**Verificação adicional (histórico vazio, DEF-10):** na execução 5, com o histórico sem check-ins, "Fazer o primeiro check-in" abriu a tela do check-in ([captura](evidencias/sprint-5/historico-01-primeiro-checkin.png)). Antes do PR #78, o botão não fazia nada.

**Verificação adicional (R10, perfil D do Quadro 19):** na tela da avaliação, com o item 9 do PHQ-9 em "Vários dias" e o resto em "Nenhuma vez", o envio grava nível CRISE sem recomendações e leva à Tela de Ajuda com CVV 188 e SAMU 192 ([captura](evidencias/sprint-5/perfild-01-tela-ajuda.png)).

"Execuções" segue a definição de ciclos da [metodologia](metodologia.md#ciclos-e-reparos). TSI-02 e TSI-04 contam as execuções 2 a 5 como repetições, sem reparo entre elas.

**Observação sobre o ambiente:** seguindo o README à risca, o ambiente de demonstração sobe **sem** o catálogo, porque o passo de seed só roda `app.seed_demo`; sem materiais, todo check-in e toda avaliação saem sem recomendações (R-S6), e o TSI-01 e o TSI-03 falham. As cinco execuções foram feitas com o seed do catálogo rodado à parte. Ver [DEF-08](defeitos.md#def-08).

### Resumo do roteiro

| Status | Casos | Quantidade |
| :-- | :-- | :--: |
| Aprovado | TU-01 a TU-07, TI-01 a TI-07, TS-01 a TS-05, TSI-01 a TSI-05 | **24** |

**Os 24 casos do roteiro estão aprovados.** Todos os automatizados passam na CI, e as pendências da Sprint 4 (TU-06, TI-03, TI-05 e TS-03) foram fechadas. Pela interface, as jornadas do check-in (TSI-01), de risco (TSI-02), da avaliação (TSI-03), da Ajuda Imediata (TSI-04) e da exclusão de conta (TSI-05) funcionam de ponta a ponta. A proposta de atualização do Quadro 26 está em [Quadro 26 da Sprint 5](quadro-26-sprint-5.md).

## Conclusão da sprint (M4)

Itens comprometidos conforme a seção 5 do [Planejamento da Sprint 5](../sprints/sprint-5.md#5-backlog-proposto-da-sprint-5). Posição em 25/11/2026, às 22h45.

| Issue | Item | Estado no GitHub | Critérios de aceite verificados | Contagem pelos critérios |
| :--: | :-- | :--: | :-- | :--: |
| #46 | Seleção conforme o Quadro 20 (DEF-02) | Fechada | PR #66; TU-06 aprovado; M1 = 100% | Concluído |
| #47 | TU-06 completo (DEF-03) | Fechada | PR #66; inativos, regra e motivo por item e teto de 2 para N2 verificados | Concluído |
| #45 | Recomendações no check-in (DEF-01) | Fechada | PR #67; TI-03 e TI-05 aprovados; `GET /api/checkins/hoje` devolve as recomendações (DP-2) | Concluído |
| #51 | Modelo e migração da Avaliacao | Fechada | PR #68; cascata a partir do usuário testada | Concluído |
| #54 | `POST /api/avaliacoes` | Fechada | PR #69; TI-06 aprovado com os perfis A a E | Concluído |
| #55 | `GET /api/avaliacoes` e `/{id}`, TS-03 | Fechada | PR #70; TS-03 aprovado; saída do `/{id}` igual à do POST (DP-3) | Concluído |
| #56 | Materiais do dia no check-in | Fechada | PR #71; testes da tela (materiais e motivos, reabertura, `target` e `rel` do link, P5 = Sim); ESLint e vitest verdes; TSI-01 aprovado | Concluído |
| #53 | Cliente de API de avaliações | Fechada | PR #72; `avaliacoes.test.ts` (8 testes no padrão de `checkins.test.ts`: criar, listar, buscar por id, 401, 404, 422 e erro de rede); ESLint e vitest verdes | Concluído |
| #60 | `DELETE /api/me` | Fechada | PR #73; TI-07 aprovado no banco de teste e repetido no ambiente de demonstração; TS-01, TS-02 e TS-04 aprovados; migração 0007 com `downgrade` e `upgrade` verificados pelo QA | Concluído |
| #58 | Tela de resultado | Fechada | PR #75; testes do perfil B (10/5, Moderada/Leve, UBS, "não é diagnóstico", 2 materiais), 404 de outro usuário, 422 e nível crise; ESLint e vitest verdes; no navegador, a tela de resultado do TSI-03 confere item a item | Concluído |
| #61 | Excluir conta (tela) | Fechada | PR #74; testes de cancelar (não exclui) e confirmar (chama a rota, limpa a sessão e redireciona); TSI-05 aprovado no navegador (login com as mesmas credenciais falha); ESLint e vitest verdes | Concluído |
| #57 | Tela da avaliação | Fechada | PR #77; testes de envio bloqueado com item sem resposta, item 9 ≥ 1 abrindo a Tela de Ajuda e envio válido levando ao resultado; botão "Preciso de ajuda agora" visível; ESLint e vitest verdes; TSI-03 aprovado | Concluído |
| #59 | Avaliações no histórico | Fechada | PR #76; testes com lista vazia, com avaliações e com erro da API; check-ins exibidos como antes; cada avaliação abre o resultado (#58); ESLint e vitest verdes | Concluído |
| #62 | Acompanhamento de QA | Fechada pelo PR destes registros | M1 a M5 registradas; TSI-01 a TSI-04 executados com evidência; nenhum defeito crítico | Concluído |
| #52 | Textos do PHQ-9 e GAD-7 e protótipo | Fechada | PR #65 mesclado na `docs`, com o protótipo do Figma linkado na página. O merge deixou marcadores de conflito no `mkdocs.yml` e o deploy falhou (DEF-09); o commit `eedab0a` corrigiu e o site foi publicado com a página | Concluído |
| #63 | Revisão da Sprint 4 e planejamento (PO) | Aberta | Faltam a retrospectiva da Sprint 4, a conferência dos 7 materiais com o Quadro 21, o quadro no GitHub Projects e a revisão da Sprint 5 | Não concluído |
| | **Total** | **15 de 16 (93,8%)** | | **15 de 16 (93,8%)** |

As duas leituras coincidem e ficam **acima da referência de 80%**. Todas as issues de desenvolvimento foram entregues: o backend inteiro, inclusive as pendências da Sprint 4, e, na interface, o check-in com materiais, a avaliação e o resultado, as avaliações no histórico e a exclusão de conta. Só a #63, do PO, segue aberta; quando ela fechar, a sprint chega a 16 de 16 (100%). Os PRs do backend foram mesclados nos dois últimos dias da sprint (24 e 25/11), e onze das quinze entregas foram mescladas no último dia, o que concentrou a conferência e o roteiro de sistema nas últimas horas.

**Critérios de replanejamento (Visão, seção 2.6):**

- **Critério 3** (duas sprints seguidas abaixo de 80%): não é acionado; as Sprints 4 (85,7%) e 5 (93,8%) ficaram acima de 80%.
- **Critério 1** (item Must não entregue): não é acionado; todos os requisitos Must previstos para a sprint foram entregues (R04, R06, R08, R09, R10 e R12).

## Integração contínua na sprint

Execuções do workflow `CI` entre 12/11 e 25/11/2026. O workflow `ci` da `docs`, que publica o site, é contado à parte, como na Sprint 4.

| Evento | Execuções | Aprovadas | Reprovadas | Canceladas |
| :-- | :--: | :--: | :--: | :--: |
| Pull request | 19 | 17 | 2 | 0 |
| Push (`developer`) | 13 | 11 | 0 | 2 |
| Push (`main`) | 1 | 1 | 0 | 0 |
| Push (`docs`, publicação do site) | 6 | 5 | 1 | 0 |

As falhas em PR (2 de 19, ou 11%, contra 26% na Sprint 4) foram no PR #67 ([execução 44953808003](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/44953808003)), no teste de integração de R-S2, e no PR #78 ([execução 45736399670](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45736399670)), na verificação de formatação (Prettier); as duas foram corrigidas no próprio PR. As duas execuções canceladas em push foram substituídas por merges seguidos na `developer` (#66 → #67 e #68 → #69). A falha na `docs` ([execução 45713457088](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45713457088)) veio do merge do PR #65 e é o DEF-09; a execução seguinte, depois do commit `eedab0a`, publicou o site. O único push na `main` foi o merge do PR #80 ([execução 45738490093](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45738490093)), aprovado com 298 testes no backend e 85 no frontend.

## Conferência dos PRs

A conferência de cada PR da sprint contra o Quadro 26 está em [Conferência dos PRs da Sprint 5](conferencia-prs-sprint-5.md).

## Pendências para a revisão e a Sprint 6

1. ~~Abrir e mesclar o PR `developer` → `main`~~: feito no PR #80 (25/11, 22h50); a CI da `main` passou.
2. Incluir o seed do catálogo no README e no job `demo` da CI (DEF-08), o único defeito aberto.
3. Sprint 6: repetir todo o roteiro de sistema (TSI-01 a TSI-05) no ciclo final, com a `main`.
4. PO: fechar a #63 (retrospectiva da Sprint 4, conferência dos 7 materiais e Quadro 21, quadro no GitHub Projects e revisão da Sprint 5), registrar o percentual da Sprint 5 no Quadro 8 e aplicar a [proposta do Quadro 26](quadro-26-sprint-5.md) na Visão.
5. Rever o processo de revisão: dos 13 PRs de código da sprint (#66 a #78), 6 tiveram aprovação registrada antes do merge (#68, #69, #73, #75, #77 e #78); 7 não tiveram (#67 só com comentário, #70, #71, #72, #74 e #76 sem revisão, e o #66 mesclado sem nova aprovação depois do pedido de mudanças). O #65, da `docs`, e o #80, da `developer` para a `main`, também entraram sem revisão, e a correção do DEF-09 foi um push direto na `docs`, sem PR ([conferência](conferencia-prs-sprint-5.md)). O #65 mostra o risco: entrou com marcadores de conflito, que um build local (`mkdocs build --strict`) teria pegado.
