# Registro de defeitos

Defeitos encontrados na conferência da Sprint 4 (posição final em 11/11/2026). Pela Visão (seção 6.1, item 4), cada defeito vira uma issue com a label `bug` e a severidade (crítica, alta, média ou baixa); depois do reparo, o caso é executado de novo e o número de ciclos é atualizado.

**Situação:** dos 5 defeitos, **2 foram corrigidos na própria sprint** (DEF-04 e DEF-05) e **3 seguem abertos** (DEF-01, DEF-02 e DEF-03). Os 3 abertos têm issue `bug`: #45 (DEF-01), #46 (DEF-02) e #47 (DEF-03).

| ID | Severidade | Título | Casos afetados | Responsável sugerido | Issue |
| :-- | :--: | :-- | :-- | :-- | :--: |
| [DEF-01](#def-01) | **Alta** | `POST /api/checkins` não gera nem grava recomendações | TI-03, TI-05 | Luiz Felipe | #45 |
| [DEF-02](#def-02) | Média | `selecionar_materiais` diverge do Quadro 20 da Visão | TU-06 | Luiz Felipe (PO decidiu em 12/11: vale o Quadro 20) | #46 |
| [DEF-03](#def-03) | Média | Testes de seleção de conteúdo não cobrem R-S1, R-S3 e R-S4 | TU-06, M1 | Luiz Felipe | parcialmente corrigido (PR #38); restante na #47 |
| [DEF-04](#def-04) | Média | Cadastro e `GET /api/me` divergem do contrato da Arquitetura | TI-01, TS-04 | Luiz Felipe, Carlos Eduardo | **corrigido** (#22, PRs #39, #41 e #42) |
| [DEF-05](#def-05) | Média | Testes de API do TS-03 não usam o banco de teste | TS-03 | Carlos Eduardo | **corrigido** (PR #39) |

**Totais por severidade (abertos):** 0 críticas, 1 alta, 2 médias, 0 baixas; 2 médias corrigidas. Total encontrado: 0 críticas, 1 alta, 4 médias, 0 baixas. Nenhum defeito crítico (um teste de segurança reprovado ou um encaminhamento errado ao usuário seria crítico).

## Critério de severidade usado

| Severidade | Critério |
| :-- | :-- |
| Crítica | Falha de teste de segurança (risco R4) ou regra que encaminha o usuário de forma errada (risco R3). |
| Alta | Requisito Must sem o resultado esperado do roteiro, sem risco imediato ao usuário. |
| Média | Divergência entre código e documento, ou lacuna de teste, que não impede o fluxo principal. |
| Baixa | Problema de forma ou de documentação sem efeito no comportamento. |

<a id="def-01"></a>
## DEF-01: `POST /api/checkins` não gera nem grava recomendações

**Severidade:** alta. **Requisitos:** R05, R06. **Casos:** TI-03 (não atendido), TI-05 (parcial). **Issue de origem:** #5 (fechada).

**Resultado esperado (Visão, Quadro 26, TI-03):** P1 = 4, P2 = 3, P3 = 1, P4 = 0, P5 = Não → 201; tags [ANSIEDADE, SONO]; 2 recomendações persistidas com materiais dessas tags e regras R-D3 e R-D4. TI-05: lista de recomendações vazia e nenhuma linha nova em `Recomendacao`.

**Resultado obtido:** 201 com apenas `{"nivel": "autocuidado", "tags": ["ansiedade", "sono"]}`. `CheckinService.create` chama `avaliar_checkin`, grava o check-in e termina; não chama `selecionar_materiais`. Não existem na `main` o modelo `Material`, a entidade `Recomendacao` (Arquitetura, Figura 6) nem as migrações correspondentes. A resposta não traz a lista de recomendações exigida pela issue #5.

**Evidência:** `backend/app/application/checkins.py` (função `create`); `backend/tests/test_checkins.py::test_ti03_create_checkin_returns_201_with_nivel_and_tags` verifica só nível e tags e, por isso, passa na CI ([execução 42691191624](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/42691191624)).

**Causa provável:** a #5 depende da #17 (concluída) e da #19 (catálogo e `Material`, mesclada depois, no PR #37). A issue foi fechada sem as recomendações.

**Para corrigir:** com o catálogo já na `main` (PR #37), criar `Recomendacao` (modelo e migração com regra e motivo, cascata a partir do usuário), integrar `selecionar_materiais` ao serviço, devolver as recomendações na resposta e completar o TI-03 e o TI-05 com as verificações do Quadro 26. Reabrir a #5 ou abrir issue nova que a referencie. Sem isso, o R06 não é entregue na Sprint 4.

<a id="def-02"></a>
## DEF-02: `selecionar_materiais` diverge do Quadro 20 da Visão

**Severidade:** média. **Caso:** TU-06 (parcial). **Requisito:** R06.

| Regra | Quadro 20 | Código em `app/rules/selecao.py` |
| :--: | :-- | :-- |
| R-S2 | Escolher o material recomendado há mais tempo; nunca recomendado primeiro; empate pelo menor id | Exclui os materiais exibidos recentemente; não ordena por tempo |
| R-S5 | Guardar a regra de origem (ex.: R-D4) e o motivo | `Sugestao.regra` recebe "R-S3" ou "R-S6" |
| R-S6 | Sem material para nenhuma tag, exibir só a orientação do nível | Completa a lista com materiais BEM_ESTAR ou sem tag |
| R-S3 | Material não se repete | A deduplicação existe, mas o rótulo "R-S3" é usado para o casamento de tags |

**Decisão do PO (12/11/2026, Visão v2.5):** o Quadro 20 permanece como está e o código se ajusta a ele, em todas as linhas: R-S2 ordena os candidatos pela data da última recomendação ao usuário (nunca recomendado primeiro; empate pelo menor id), sem janela de bloqueio; R-S5 grava a regra de origem da tag (R-D2 a R-D6 ou R-A2 a R-A4) e o motivo correspondente; R-S6 não completa a lista com outros materiais. Os testes do TU-06 devem seguir o Quadro 20, e não o código atual. A divergência já havia sido apontada na revisão do PR #32.

<a id="def-03"></a>
## DEF-03: testes de seleção de conteúdo não cobrem R-S1, R-S3 e R-S4

**Severidade:** média. **Caso:** TU-06; **métrica** M1 (R-S abaixo de 100%). **Issue de origem:** #17, cujo critério de aceite exige "toda linha de R-D1 a R-D6 e de R-S1 a R-S6 com ao menos um teste".

**Faltam:** (a) ordem de prioridade com duas ou mais tags (R-S1); (b) material com duas tags geradas aparecendo uma só vez (R-S3); (c) teto de 3 materiais, de 2 para N2 e descarte pela ordem de prioridade (R-S4); (d) exclusão de material inativo e presença de regra e motivo em cada item, previstos no resultado esperado do TU-06.

Os testes de (a), (b) e o teto geral de (c) foram escritos e mesclados no PR #38; (d) e o teto de 2 para N2 seguem pendentes. Estes testes não dependem da decisão do DEF-02 (exceto R-S5) e devem ser escritos primeiro. Ver [matriz regra × teste](matriz-regras-testes.md).

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
