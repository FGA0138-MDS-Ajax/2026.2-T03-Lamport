# Registro de defeitos

Defeitos encontrados na conferência da Sprint 4 (posição de 10/11/2026). Pela Visão (seção 6.1, item 4), cada defeito vira uma issue com a label `bug` e a severidade (crítica, alta, média ou baixa); depois do reparo, o caso é executado de novo e o número de ciclos é atualizado.

**Situação:** as issues ainda **não foram abertas**; os textos abaixo estão prontos para isso. Nenhuma issue `bug` existe hoje no repositório (M5 = 0 abertas, 5 propostas).

| ID | Severidade | Título | Casos afetados | Responsável sugerido | Issue |
| :-- | :--: | :-- | :-- | :-- | :--: |
| [DEF-01](#def-01) | **Alta** | `POST /api/checkins` não gera nem grava recomendações | TI-03, TI-05 | Luiz Felipe | a abrir |
| [DEF-02](#def-02) | Média | `selecionar_materiais` diverge do Quadro 20 da Visão | TU-06 | PO decide; Luiz Felipe | a abrir |
| [DEF-03](#def-03) | Média | Testes de seleção de conteúdo não cobrem R-S1, R-S3 e R-S4 | TU-06, M1 | Luiz Felipe | a abrir |
| [DEF-04](#def-04) | Média | Cadastro e `GET /api/me` divergem do contrato da Arquitetura | TI-01, TS-04 | Luiz Felipe, Carlos Eduardo | já tratado na #22 |
| [DEF-05](#def-05) | Média | Testes de API do TS-03 não usam o banco de teste | TS-03 | Carlos Eduardo | a abrir |

**Totais por severidade:** 0 críticas, 1 alta, 4 médias, 0 baixas. Nenhum defeito crítico (um teste de segurança reprovado ou um encaminhamento errado ao usuário seria crítico).

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

**Causa provável:** a #5 depende da #17 (concluída) e da #19 (catálogo e `Material`, ainda em PR). A issue foi fechada sem as recomendações.

**Para corrigir:** depois do merge do PR #37, criar `Recomendacao` (modelo e migração com regra e motivo, cascata a partir do usuário), integrar `selecionar_materiais` ao serviço, devolver as recomendações na resposta e completar o TI-03 e o TI-05 com as verificações do Quadro 26. Reabrir a #5 ou abrir issue nova que a referencie. Sem isso, o R06 não é entregue na Sprint 4.

<a id="def-02"></a>
## DEF-02: `selecionar_materiais` diverge do Quadro 20 da Visão

**Severidade:** média. **Caso:** TU-06 (parcial). **Requisito:** R06.

| Regra | Quadro 20 | Código em `app/rules/selecao.py` |
| :--: | :-- | :-- |
| R-S2 | Escolher o material recomendado há mais tempo; nunca recomendado primeiro; empate pelo menor id | Exclui os materiais exibidos recentemente; não ordena por tempo |
| R-S5 | Guardar a regra de origem (ex.: R-D4) e o motivo | `Sugestao.regra` recebe "R-S3" ou "R-S6" |
| R-S6 | Sem material para nenhuma tag, exibir só a orientação do nível | Completa a lista com materiais BEM_ESTAR ou sem tag |
| R-S3 | Material não se repete | A deduplicação existe, mas o rótulo "R-S3" é usado para o casamento de tags |

**Decisão necessária (PO):** como os documentos são a fonte da verdade, o PO decide, para cada linha, entre atualizar o Quadro 20 em nova versão da Visão ou ajustar o código. Até lá não se altera o teste para acompanhar o código. A divergência já havia sido apontada na revisão do PR #32.

<a id="def-03"></a>
## DEF-03: testes de seleção de conteúdo não cobrem R-S1, R-S3 e R-S4

**Severidade:** média. **Caso:** TU-06; **métrica** M1 (R-S abaixo de 100%). **Issue de origem:** #17, cujo critério de aceite exige "toda linha de R-D1 a R-D6 e de R-S1 a R-S6 com ao menos um teste".

**Faltam:** (a) ordem de prioridade com duas ou mais tags (R-S1); (b) material com duas tags geradas aparecendo uma só vez (R-S3); (c) teto de 3 materiais, de 2 para N2 e descarte pela ordem de prioridade (R-S4); (d) exclusão de material inativo e presença de regra e motivo em cada item, previstos no resultado esperado do TU-06.

Os testes de (a), (b) e o teto geral de (c) foram escritos na branch `test/regras-selecao-rs1-rs3-rs4` (sem merge); (d) e o teto de 2 para N2 seguem pendentes. Estes testes não dependem da decisão do DEF-02 (exceto R-S5) e devem ser escritos primeiro. Ver [matriz regra × teste](matriz-regras-testes.md).

<a id="def-04"></a>
## DEF-04: cadastro e `GET /api/me` divergem do contrato da Arquitetura

**Severidade:** média. **Casos:** TI-01 (não executável como escrito), TS-04 (parcial). **Tratado na issue #22** (aberta, sem PR).

- A declaração de maioridade (`maior_de_idade`) não existe no cadastro; o TI-01 exige 422 sem a declaração 18+.
- As rotas são `/api/auth/register` e `/api/users/me`; o Quadro 6 define `/api/auth/cadastro` e `/api/me`.
- `GET /api/users/me` devolve `id`, `email`, `role` e `created_at`; o TS-04 exige apenas `id`, `email` e `criado_em`.

Sugestão: manter o acompanhamento na #22, acrescentando a label `bug` e a severidade média, em vez de abrir uma issue duplicada.

<a id="def-05"></a>
## DEF-05: testes de API do TS-03 não usam o banco de teste

**Severidade:** média. **Caso:** TS-03 (parcial). **Issue de origem:** #6 (PR #15).

A issue #6 pede "testes de integração no PostgreSQL de teste cobrindo ordem, limite e isolamento". Em `test_checkins_get.py`, os testes de API (`test_api_list_checkins_isolation_ts_03`, `test_api_get_checkin_by_id_other_user_returns_404`) substituem o repositório por `FakeCheckinRepository` e a sessão por um `MagicMock`. O isolamento no nível do banco só é verificado em `test_checkin_repository.py`. Se o filtro por usuário fosse removido da rota ou da consulta de integração, a falha poderia passar despercebida. O risco R4 (vazamento de dados) depende desse teste.

**Para corrigir:** acrescentar versão do teste que use o `client` e as fixtures de banco do `conftest.py` (como `test_checkins.py`), com os usuários A e B.

## Comandos para abrir as issues

Não foram executados. As labels `severidade-alta` e `severidade-media` ainda não existem no repositório, e `bug` já existe.

```bash
gh label create "severidade-alta"  --color D93F0B --description "Defeito de severidade alta"
gh label create "severidade-media" --color FBCA04 --description "Defeito de severidade média"

gh issue create --title "[Bug] POST /api/checkins não gera nem grava recomendações (TI-03, TI-05)"   --label bug --label severidade-alta --assignee LuizFelipe81   --body "Ver DEF-01 em docs/metricas/defeitos.md (resultado esperado, obtido, evidência e correção)."

gh issue create --title "[Bug] selecionar_materiais diverge do Quadro 20 (R-S2, R-S3, R-S5, R-S6)"   --label bug --label severidade-media   --body "Ver DEF-02 em docs/metricas/defeitos.md. Exige decisão do PO: atualizar o Quadro 20 ou o código."

gh issue create --title "[Bug] Testes de seleção não cobrem R-S1, R-S3 e R-S4 (TU-06, M1)"   --label bug --label severidade-media --assignee LuizFelipe81   --body "Ver DEF-03 em docs/metricas/defeitos.md."

gh issue create --title "[Bug] TS-03: testes de API sem o banco de teste"   --label bug --label severidade-media --assignee CarlosA84   --body "Ver DEF-05 em docs/metricas/defeitos.md."

gh issue edit 22 --add-label bug --add-label severidade-media   # DEF-04
```
