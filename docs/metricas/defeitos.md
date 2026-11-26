# Registro de defeitos

Defeitos encontrados pelo QA nas conferências das Sprints 4 e 5. Pela Visão (seção 6.1, item 4), cada defeito vira uma issue com a label `bug` e a severidade (crítica, alta, média ou baixa); depois do reparo, o caso é executado de novo e o número de ciclos é atualizado. Quando uma issue aberta já cobre o defeito, ela é usada em vez de abrir uma duplicada (precedente do DEF-04).

**Situação em 25/11/2026, às 22h45 (fim da Sprint 5):** dos 10 defeitos registrados, **9 estão corrigidos** (DEF-01 a DEF-07, DEF-09 e DEF-10) e **1 segue aberto** (DEF-08, médio), que ainda não tem issue. Nenhuma issue `bug` está aberta.

| ID | Severidade | Título | Casos afetados | Sprint | Issue | Situação |
| :-- | :--: | :-- | :-- | :--: | :--: | :--: |
| [DEF-08](#def-08) | **Média** | Ambiente de demonstração sobe sem o catálogo de materiais | TSI-01, TSI-03 | 5 | a abrir | **Aberto** |
| [DEF-10](#def-10) | Média | Botão "Fazer o primeiro check-in" do histórico não faz nada | — (histórico vazio) | 5 | — (PR #78) | Corrigido (PR #78) |
| [DEF-09](#def-09) | Baixa | `mkdocs.yml` com marcadores de conflito; site da documentação não publica | — | 5 | #52 | Corrigido (commit `eedab0a`) |
| [DEF-07](#def-07) | Alta | Não há tela de avaliação nem de resultado | TSI-03 | 5 | #57, #58 | Corrigido (PRs #75 e #77) |
| [DEF-06](#def-06) | Alta | Materiais e motivo não aparecem depois do check-in | TSI-01 | 5 | #56 | Corrigido (PR #71) |
| [DEF-01](#def-01) | Alta | `POST /api/checkins` não gera nem grava recomendações | TI-03, TI-05 | 4 | #45 | Corrigido (PR #67) |
| [DEF-02](#def-02) | Média | `selecionar_materiais` diverge do Quadro 20 da Visão | TU-06 | 4 | #46 | Corrigido (PR #66) |
| [DEF-03](#def-03) | Média | Testes de seleção não cobrem inativos nem regra e motivo por item | TU-06, M1 | 4 | #47 | Corrigido (PRs #38 e #66) |
| [DEF-04](#def-04) | Média | Cadastro e `GET /api/me` divergem do contrato da Arquitetura | TI-01, TS-04 | 4 | #22 | Corrigido (PRs #39, #41 e #42) |
| [DEF-05](#def-05) | Média | Testes de API do TS-03 não usam o banco de teste | TS-03 | 4 | — | Corrigido (PR #39) |

**Totais por severidade (abertos):** 0 críticas, 0 altas, 1 média, 0 baixas. **Total encontrado:** 0 críticas, 3 altas, 6 médias, 1 baixa. Nenhum defeito crítico: as jornadas do check-in (TSI-01), de risco (TSI-02) e da Ajuda Imediata sem login (TSI-04) foram aprovadas, nenhum teste de segurança falha e as regras em uso encaminham corretamente. O aviso "não é diagnóstico" (risco R2) já aparece na tela de resultado.

## Critério de severidade usado

| Severidade | Critério |
| :-- | :-- |
| Crítica | Falha de teste de segurança (risco R4) ou regra que encaminha o usuário de forma errada (risco R3). |
| Alta | Requisito Must sem o resultado esperado do roteiro, sem risco imediato ao usuário. |
| Média | Divergência entre código e documento, ou lacuna de teste, que não impede o fluxo principal. |
| Baixa | Problema de forma ou de documentação sem efeito no comportamento. |

<a id="def-06"></a>
## DEF-06: materiais e motivo não aparecem depois do check-in

**Corrigido na Sprint 5** pelo PR #71 (issue #56, fechada): na execução 2 do ciclo 1 (25/11, 19h32), o TSI-01 foi aprovado, com material, motivo, link para a fonte oficial e histórico ([evidências](sprint-5.md#roteiro-de-sistema-ciclo-1)).

**Severidade:** alta. **Requisito:** R06 (Must). **Caso:** TSI-01 (não atendido na execução 1). **Issue:** #56. **Encontrado em:** 25/11/2026, execução 1 do ciclo 1 do roteiro de sistema.

**Resultado esperado (Visão, Quadro 26, TSI-01):** cadastro → login → check-in com P1 = 2 → materiais de HUMOR com motivo → link abre a fonte oficial → histórico mostra o check-in.

**Resultado obtido:** o `POST /api/checkins` devolve 201 com 1 material de HUMOR ("Depressão – Saúde de A a Z", regra R-D2, motivo "Você indicou humor ruim ou muito ruim hoje."), mas a tela do check-in volta à página inicial sem exibir material nem motivo. Sem o material na tela, o passo do link não é executável. O histórico mostra o check-in com o tema Humor.

**Evidência:** [após o envio](evidencias/sprint-5/tsi01-execucao1-apos-checkin.png); resposta da API no [registro da execução 1](evidencias/sprint-5/execucao-1.txt); `frontend/src/pages/DailyCheckin.tsx` navega para `/` depois do envio.

**Causa:** a tela da #56 ainda não estava na `developer`; o backend da #45 já estava pronto.

<a id="def-07"></a>
## DEF-07: não há tela de avaliação nem de resultado

**Corrigido na Sprint 5:** a tela de resultado entrou no PR #75 (#58) e a tela da avaliação no PR #77 (#57). Na execução 4 do ciclo 1 (25/11, 22h24), o TSI-03 foi aprovado de ponta a ponta pela interface ([resultado](evidencias/sprint-5/tsi03-06-resultado.png)).

**Severidade:** alta. **Requisitos:** R08 e R09 (Must). **Caso:** TSI-03 (não atendido nas execuções 1 e 2; parcial na 3). **Issues:** #57 (PR #77) e #58 (PR #75), fechadas. **Encontrado em:** 25/11/2026, ciclo 1.

**Resultado esperado (TSI-03, perfil B):** escores 10/5, faixa moderada, orientação de procurar a UBS, aviso "não é diagnóstico" e 2 materiais.

**Resultado obtido:** depois do login, a página inicial só oferece o check-in; `/avaliacao` e `/avaliacoes` mostram "Página não encontrada". Pela API, o mesmo perfil devolve o resultado esperado ([resposta](evidencias/sprint-5/tsi03-api-perfil-b.json)), então a falha está só na interface.

**Evidência (execuções 1 a 3):** [página inicial](evidencias/sprint-5/tsi03-03-logado.png), [rota inexistente](evidencias/sprint-5/tsi03-04-rota-avaliacao.png). O aviso "não é diagnóstico" (risco R2), ponto de maior risco do caso, aparece no topo do resultado desde o PR #75.

<a id="def-08"></a>
## DEF-08: ambiente de demonstração sobe sem o catálogo de materiais

**Severidade:** média. **Casos:** TSI-01 e TSI-03 (pré-condição do Quadro 25: "catálogo real"). **Issue:** a abrir. **Encontrado em:** 25/11/2026, ao preparar o ciclo 1.

**Resultado esperado (Visão, Quadro 25):** o ambiente de demonstração roda "com catálogo real e usuários fictícios".

**Resultado obtido:** o README manda rodar só `python -m app.seed_demo`, que cria usuários e não carrega materiais; o próprio README diz que o seed do catálogo "ainda não foi integrado", embora `app.seed_materiais` exista desde o PR #37. O job `demo` da CI segue o README e também não carrega o catálogo. Seguindo os passos documentados, todo check-in e toda avaliação saem sem recomendações (R-S6), e o TSI-01 falha mesmo com a tela da #56.

**Para corrigir:** acrescentar `docker compose exec api python -m app.seed_materiais` ao passo 3 do README e ao job `demo` da CI, e retirar o aviso de que o seed não foi integrado. As quatro execuções do ciclo 1 foram feitas rodando esse comando à parte.

<a id="def-10"></a>
## DEF-10: botão "Fazer o primeiro check-in" do histórico não faz nada

**Severidade:** média (lacuna de teste que não impede o fluxo principal: o check-in segue acessível pela página inicial). **Requisito:** R12. **Origem:** PR #29 (Sprint 4, commit `b88a719`). **Encontrado em:** 25/11/2026, pela equipe, depois da execução 4 do ciclo 1. **Corrigido** no PR #78, sem issue.

**Resultado obtido antes da correção:** no histórico de quem ainda não fez check-in, o botão "Fazer o primeiro check-in" não tinha ação ao clicar.

**Correção e verificação:** o PR #78 faz o botão levar à tela do check-in; na execução 5 do ciclo 1 (25/11, 22h42), o clique abriu "Check-in diário" ([captura](evidencias/sprint-5/historico-01-primeiro-checkin.png)).

**Por que passou:** nenhum teste clicava no botão, e o roteiro de sistema não passa pelo histórico vazio. O PR #78 também não acrescenta teste; recomenda-se um teste de clique em `HistoryPage.test.tsx`.

<a id="def-09"></a>
## DEF-09: `mkdocs.yml` com marcadores de conflito; site da documentação não publica

**Severidade:** baixa (documentação, sem efeito no comportamento do produto). **Issue de origem:** #52 (fechada pelo PR #65). **Encontrado em:** 25/11/2026. **Corrigido** em 25/11/2026, às 19h53, pelo commit `eedab0a` (push direto na `docs`, sem PR); a publicação seguinte ([execução 45716938818](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45716938818)) foi aprovada e o site passou a mostrar a página da #52.

**Resultado esperado (critério de aceite da #52):** "Página publicada por PR na branch `docs`".

**Resultado obtido:** o merge do PR #65 deixou no `mkdocs.yml` os marcadores `<<<<<<< HEAD`, `=======` e `>>>>>>> origin/docs` em volta das entradas "Vocabulário da avaliação" e "Protótipo do check-in". O `mkdocs gh-deploy` falha ao ler a configuração ([execução 45713457088](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/45713457088)), e o site fica parado na versão anterior, sem a página da #52.

**Correção:** os marcadores foram retirados, mantendo as duas entradas do menu; `mkdocs build --strict` passa sem avisos. Para evitar que se repita: rodar `mkdocs build --strict` antes do merge e incluí-lo em um job da CI em PR para a `docs` (hoje a CI da `docs` só roda depois do push).

<a id="def-01"></a>
## DEF-01: `POST /api/checkins` não gera nem grava recomendações

**Corrigido na Sprint 5** pelo PR #67 (issue #45, fechada): TI-03 e TI-05 aprovados, com as recomendações conferidas na resposta e no banco.

**Severidade:** alta. **Requisitos:** R05, R06. **Casos:** TI-03 (não atendido), TI-05 (parcial). **Issue de origem:** #5 (fechada).

**Resultado esperado (Visão, Quadro 26, TI-03):** P1 = 4, P2 = 3, P3 = 1, P4 = 0, P5 = Não → 201; tags [ANSIEDADE, SONO]; 2 recomendações persistidas com materiais dessas tags e regras R-D3 e R-D4. TI-05: lista de recomendações vazia e nenhuma linha nova em `Recomendacao`.

**Resultado obtido:** 201 com apenas `{"nivel": "autocuidado", "tags": ["ansiedade", "sono"]}`. `CheckinService.create` chama `avaliar_checkin`, grava o check-in e termina; não chama `selecionar_materiais`. O modelo `Material` e a tabela `materiais` já estão na `main` (PR #37), mas não existem a entidade `Recomendacao` (Arquitetura, Figura 6) nem a migração correspondente. A resposta não traz a lista de recomendações exigida pela issue #5.

**Evidência:** `backend/app/application/checkins.py` (função `create`); `backend/tests/test_checkins.py::test_ti03_create_checkin_returns_201_with_nivel_and_tags` verifica só nível e tags e, por isso, passa na CI ([execução 42691191624](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42691191624)).

**Causa provável:** a #5 depende da #17 (concluída) e da #19 (catálogo e `Material`, mesclada depois, no PR #37). A issue foi fechada sem as recomendações.

**Para corrigir:** com o catálogo já na `main` (PR #37), criar `Recomendacao` (modelo e migração com regra e motivo, cascata a partir do usuário), integrar `selecionar_materiais` ao serviço, devolver as recomendações na resposta e completar o TI-03 e o TI-05 com as verificações do Quadro 26. Reabrir a #5 ou abrir issue nova que a referencie. Sem isso, o R06 não é entregue na Sprint 4.

<a id="def-02"></a>
## DEF-02: `selecionar_materiais` diverge do Quadro 20 da Visão

**Corrigido na Sprint 5** pelo PR #66 (issue #46, fechada): R-S1 a R-S6 aderentes ao Quadro 20; TU-06 aprovado.

**Severidade:** média. **Caso:** TU-06 (parcial). **Requisitos:** R06 e R09.

| Regra | Quadro 20 | Código em `app/rules/selecao.py` |
| :--: | :-- | :-- |
| R-S1 | Buscar os materiais ativos de cada tag na ordem AJUDA_PROFISSIONAL → ANSIEDADE → HUMOR → ESTRESSE → SONO → BEM_ESTAR | Usa a ordem do check-in, sem AJUDA_PROFISSIONAL: só com essa tag (N2), devolve materiais de BEM_ESTAR pelo fallback; `MaterialCatalogo` não tem o indicador de ativo |
| R-S2 | Escolher o material recomendado há mais tempo; nunca recomendado primeiro; empate pelo menor id | Exclui os materiais exibidos recentemente; não ordena por tempo |
| R-S5 | Guardar a regra de origem (ex.: R-D4) e o motivo | `Sugestao.regra` recebe "R-S3" ou "R-S6" |
| R-S6 | Sem material para nenhuma tag, exibir só a orientação do nível | Completa a lista com materiais BEM_ESTAR ou sem tag |
| R-S3 | Material não se repete | A deduplicação existe, mas o rótulo "R-S3" é usado para o casamento de tags |

**Decisão do PO (12/11/2026, registrada na Visão v2.6):** o Quadro 20 permanece como está e o código se ajusta a ele em todas as linhas divergentes: R-S1 inclui AJUDA_PROFISSIONAL na ordem de prioridade e só considera materiais ativos; R-S2 ordena os candidatos pela data da última recomendação ao usuário (nunca recomendado primeiro; empate pelo menor id), sem janela de bloqueio; R-S3 continua como deduplicação, sem ser usada como rótulo do casamento de tags; R-S5 grava a regra de origem da tag (R-D2 a R-D6 ou R-A2 a R-A4) e o motivo correspondente; R-S6 não completa a lista com outros materiais. Os testes do TU-06 devem seguir o Quadro 20, e não o código atual. A divergência já havia sido apontada na revisão do PR #32.

**R-S1 não depende de decisão:** o Quadro 20 e a ordem usada em `app/rules/avaliacao.py` já incluem AJUDA_PROFISSIONAL, então o ajuste é no código. Hoje a seleção não é chamada pelo sistema (DEF-01), por isso a severidade segue média. Se ela for ligada à avaliação (Sprint 5) sem essa correção, quem estiver em N2 recebe materiais de BEM_ESTAR em vez de AJUDA_PROFISSIONAL, o que, pelo critério desta página, é defeito crítico (risco R3).

<a id="def-03"></a>
## DEF-03: testes de seleção não cobrem inativos nem regra e motivo por item

**Corrigido na Sprint 5** pelo PR #66 (issue #47, fechada): inativos, regra e motivo por item e teto de 2 para N2 verificados; M1 = 100%.

**Severidade:** média. **Caso:** TU-06; **métrica** M1 (R-S abaixo de 100%). **Issue de origem:** #17, cujo critério de aceite exige "toda linha de R-D1 a R-D6 e de R-S1 a R-S6 com ao menos um teste".

**Faltavam:** (a) ordem de prioridade com duas ou mais tags (R-S1); (b) material com duas tags geradas aparecendo uma só vez (R-S3); (c) teto de 3 materiais, de 2 para N2 e descarte pela ordem de prioridade (R-S4); (d) exclusão de material inativo e presença de regra e motivo em cada item, previstos no resultado esperado do TU-06.

Os testes de (a), (b) e o teto geral de (c) foram escritos e mesclados no PR #38; (d) e o teto de 2 para N2 seguem pendentes. O teste de (a) usa só as tags do check-in; a ordem com AJUDA_PROFISSIONAL está no [DEF-02](#def-02). Estes testes não dependem da decisão do DEF-02 (exceto R-S5) e devem ser escritos primeiro. Ver [matriz regra × teste](matriz-regras-testes.md).

<a id="def-04"></a>
## DEF-04: cadastro e `GET /api/me` divergem do contrato da Arquitetura

**Severidade:** média. **Casos:** TI-01 (não executável como escrito), TS-04 (parcial). **Corrigido na issue #22** (fechada) pelos PRs #39, #41 e #42; as decisões do PO estão na Visão e na Arquitetura v2.3 (PR #40).

**Situação final:** o cadastro exige `maior_de_idade` (422 sem ela); as rotas são `/api/auth/cadastro` e `/api/me`; `GET /api/me` devolve só `id`, `email` e `criado_em`; os campos de entrada estão em português (`senha`, `aceite_termos`), conforme a v2.3. TI-01 e TS-04 passam a **Aprovado**.

**Histórico do defeito:**

- A declaração de maioridade (`maior_de_idade`) não existe no cadastro; o TI-01 exige 422 sem a declaração 18+.
- As rotas são `/api/auth/register` e `/api/users/me`; o Quadro 6 define `/api/auth/cadastro` e `/api/me`.
- `GET /api/users/me` devolve `id`, `email`, `role` e `created_at`; o TS-04 exige apenas `id`, `email` e `criado_em`.

A #22 já cobria o defeito; não foi aberta issue duplicada.

<a id="def-05"></a>
## DEF-05: testes de API do TS-03 não usam o banco de teste

**Severidade:** média. **Caso:** TS-03 (parcial). **Issue de origem:** #6 (PR #15). **Corrigido** no PR #39 com `backend/tests/test_ts03_isolamento.py` (5 testes com o `client` e o banco de teste, usuários A e B). A parte de avaliações do TS-03 segue na Sprint 5.

A issue #6 pede "testes de integração no PostgreSQL de teste cobrindo ordem, limite e isolamento". Em `test_checkins_get.py`, os testes de API (`test_api_list_checkins_isolation_ts_03`, `test_api_get_checkin_by_id_other_user_returns_404`) substituem o repositório por `FakeCheckinRepository` e a sessão por um `MagicMock`. O isolamento no nível do banco só é verificado em `test_checkin_repository.py`. Se o filtro por usuário fosse removido da rota ou da consulta de integração, a falha poderia passar despercebida. O risco R4 (vazamento de dados) depende desse teste.

**Correção aplicada:** versão do teste que usa o `client` e as fixtures de banco do `conftest.py`, com os usuários A e B.
