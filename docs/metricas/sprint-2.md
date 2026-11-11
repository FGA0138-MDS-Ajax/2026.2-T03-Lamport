# Sprint 2: Base do MVP (01/10 a 14/10/2026)

Registro retroativo, feito a partir do histórico do GitHub. Entregáveis do Quadro 8 da Visão: Documento de Arquitetura v1.1; estrutura dos repositórios; cadastro e login (R01, R02).

## Métricas

| Métrica | Valor | Observação |
| :-- | :--: | :-- |
| M1. Cobertura das tabelas de regras | n/a (0 de 16) | As tabelas R-D, R-A e R-S passam a existir na Visão v2.0, de 15/10, e o módulo de regras só entra na Sprint 4. |
| M2. Aprovação dos testes automatizados | **100%** (35 de 35 no pytest) | Última execução na `developer` após o merge do PR #1 (14/10): [execução 38571078720](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/actions/runs/38571078720). Frontend: 20 de 20 no vitest. |
| M3. Testes de segurança aprovados | n/a | O roteiro TS-01 a TS-05 só passa a ser executado na Sprint 4. Havia testes de autenticação (token inválido, expirado e com outra chave), mas sem vínculo com o roteiro. |
| M4. Conclusão da sprint | **100%** (3 de 3 itens) | Ver abaixo. O registro no Quadro 8 é do PO (issue #12). |
| M5. Defeitos abertos por severidade | 0 críticos, 0 altos, 0 médios, 0 baixos | Nenhuma issue `bug` foi aberta no período. |

## Itens comprometidos (M4)

| Item | Situação | Evidência |
| :-- | :--: | :-- |
| Documento de Arquitetura v1.1 | Concluído | Versão de 07/10/2026 ([Histórico de versões](../historico-versoes.md)). |
| Estrutura dos repositórios | Concluído | Repositório com `backend/`, `frontend/` e CI desde o PR #1. |
| Cadastro e login (R01, R02) | Concluído | PR #1 mesclado em 14/10. As divergências com a Arquitetura estão na issue #22. |

Cadastro e login foram contados como concluídos porque o PR #1 foi aceito e mesclado na sprint. As divergências com a Arquitetura continuam sendo tratadas como pendência na issue #22 (Sprint 4), sem alterar o percentual da Sprint 2.

## Integração contínua

| Evento | Execuções | Aprovadas | Reprovadas |
| :-- | :--: | :--: | :--: |
| Pull request | 4 | 4 | 0 |
| Push (`developer`) | 1 | 1 | 0 |

A CI (lint, testes e build do backend e do frontend) foi criada em 13/10 (commit `35c13a3`), no penúltimo dia da sprint.

## Análise

- A sprint entregou todos os itens comprometidos. A aderência do cadastro e do login à Arquitetura ficou como pendência registrada na issue #22 e não reduz o percentual.
