# Metodologia de coleta

Esta página descreve como as métricas M1 a M5 do GQM (Visão, Quadro 23) foram coletadas, para que qualquer integrante repita a coleta e chegue aos mesmos números. A responsabilidade pela coleta é do QA (Visão, Quadro 7).

## Fontes

| Fonte | O que fornece | Como consultar |
| :-- | :-- | :-- |
| GitHub Actions | Execuções da CI (backend, frontend, demo) e total de testes aprovados | `gh run list` e `gh run view <id> --log` |
| Pull requests | Data de merge, revisões e reparos de cada entrega | `gh pr list --state all` |
| Issues | Itens comprometidos na sprint, estado e defeitos (label `bug`) | `gh issue list --state all` |
| Código da `main` | Existência e conteúdo dos testes, usados na matriz regra × teste | Leitura dos arquivos em `backend/tests/` |
| Visão v2.2 | Planejamento (Quadro 8), regras (Quadros 16, 18 e 20) e roteiro (Quadro 26) | `docs/visao-produto-projeto.md` |

## Definição de cada métrica

| Métrica | Como foi calculada neste registro |
| :-- | :-- |
| **M1** – Cobertura das tabelas de regras | Total de linhas: 16 (R-D1 a R-D6, R-A1 a R-A4 e R-S1 a R-S6). Uma linha conta como coberta quando existe teste que verifica o comportamento descrito **no Quadro da Visão**. Teste que existe mas verifica comportamento diferente do Quadro é anotado à parte e não conta. O valor pela leitura literal da fórmula (qualquer teste associado à linha) é informado entre parênteses. |
| **M2** – Aprovação dos testes automatizados | Testes aprovados ÷ executados no pytest, na última execução da CI na `main` (ou no PR indicado) da sprint. O pytest é a única suíte que contém os testes TU, TI e TS. O resultado do vitest (frontend) é informado como complemento. |
| **M3** – Testes de segurança aprovados | Casos TS-01 a TS-05 com **todos** os critérios do Quadro 26 verificados por teste aprovado ÷ 5. Caso com teste verde mas critério sem verificação fica como "Parcial" e não conta. |
| **M4** – Conclusão da sprint | Itens concluídos ÷ comprometidos. Os itens comprometidos são os do Quadro 8 (Sprints 2 e 3) e as issues listadas na issue #12 (Sprint 4). "Concluído" é o item entregue e aceito sem pendência. Para a Sprint 4 há duas leituras: pelo estado da issue no GitHub e pelos critérios de aceite verificados pelo QA. |
| **M5** – Defeitos abertos por severidade | Issues abertas com a label `bug`, por severidade. Defeitos encontrados na conferência que ainda não viraram issue estão em [Defeitos](defeitos.md) e são contados à parte, como "propostos". |

## Status dos casos de teste

| Status | Significado |
| :-- | :-- |
| **Aprovado** | Existe teste automatizado que verifica todos os critérios do caso e ele passa na CI. |
| **Parcial** | O teste passa, mas parte dos critérios do caso não é verificada, por falta de teste ou porque a funcionalidade ainda não existe. |
| **Não atendido** | O resultado esperado do caso não é produzido pelo sistema, embora algum teste de mesmo nome possa estar verde. |
| **Pendente** | O código ou o teste ainda não está na `main` (PR aberto). |
| **Não executado** | Caso previsto para sprint posterior. |

## Ciclos e reparos

- **Ciclo**: cada execução do caso até o resultado final registrado. Um caso aprovado de primeira tem 1 ciclo.
- **Reparo**: alteração feita depois de uma falha ou de um pedido de mudança na revisão, registrada pelo número do PR.

## Limitações desta coleta

1. A CI executa `pytest` sem o modo detalhado e não publica relatório por caso. A evidência de cada caso é, portanto, o link da execução na CI (que prova a aprovação da suíte inteira) somado ao teste identificado no código. Recomendação: publicar `pytest -ra --junitxml` como artefato da CI.
2. O QA não dispõe de PostgreSQL local nesta coleta. Os testes de regras (sem banco) foram também executados localmente; os de integração e segurança foram conferidos pelo log da CI.
3. As Sprints 2 e 3 são reconstruídas depois do fim, a partir do histórico do GitHub. Nelas só existem dados de CI a partir de 13/10/2026 e não havia roteiro de testes executável (os casos TU, TI e TS entram a partir da Sprint 4).
4. Nenhuma issue do repositório usa as labels `sprint-N`, `qualidade`, `seguranca` nem de severidade, embora as issues as prevejam. Por isso M5 e M4 não puderam ser obtidos por filtro de label e foram conferidos issue a issue.

## Reprodução

```bash
# Execuções da CI de um intervalo
gh run list --workflow CI --limit 300 --json databaseId,event,headBranch,conclusion,createdAt

# Total de testes da suíte em uma execução
gh run view <id> --log --job <id-do-job-backend> | grep "passed"

# Defeitos abertos por severidade
gh issue list --label bug --state open --json number,title,labels

# Testes de regras, sem banco (exige o ambiente do backend)
cd backend && pytest --noconftest tests/test_rules_avaliacao.py tests/test_rules_checkin.py -q
```
