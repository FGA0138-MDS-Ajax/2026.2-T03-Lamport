# Matriz regra × teste (M1)

Posição em **10/11/2026**, `main` no commit `faac2cf` (PR #35). O oráculo são os Quadros 16, 18 e 20 da Visão v2.2. Cada linha das tabelas de regras deve ter ao menos um teste que verifique o comportamento do Quadro (Visão, seção 6.1).

**Resultado: 10 de 16 linhas cobertas, M1 = 62,5%** (valor esperado: 100%). Pela leitura literal da fórmula, contando também testes que verificam comportamento diferente do Quadro, seriam 12 de 16 (75%).

## R-D: check-in diário (Quadro 16)

Testes em `backend/tests/test_rules_checkin.py`.

| Regra | Condição | Teste | Situação |
| :--: | :-- | :-- | :--: |
| R-D1 | P5 = Sim: CRISE, sem tags, precedência | `test_rd1_risk_takes_precedence_and_has_no_tags`; `test_ti05_risk_answer_returns_crise_without_tags` (API) | Coberta |
| R-D2 | P1 ≤ 2 → HUMOR | `test_thresholds` (P1 = 2 aciona; P1 = 3 não aciona) | Coberta |
| R-D3 | P2 ≥ 2 → ANSIEDADE | `test_thresholds` (P2 = 2 e P2 = 1) | Coberta |
| R-D4 | P3 ≤ 2 → SONO | `test_thresholds` (P3 = 2 e P3 = 3) | Coberta |
| R-D5 | P4 ≥ 2 → ESTRESSE | `test_thresholds` (P4 = 2 e P4 = 1) | Coberta |
| R-D6 | Nenhuma de R-D2 a R-D5 → BEM_ESTAR | `test_thresholds`; `test_unanswered_question_does_not_trigger_its_rule` | Coberta |

Também cobertos: resposta nula não aciona a regra (TU-05), combinação de todas as regras na ordem de prioridade e o exemplo do TI-03 (`test_example_from_ti03`). **6 de 6.**

## R-A: avaliação quinzenal (Quadro 18)

Testes em `backend/tests/test_rules_avaliacao.py`.

| Regra | Condição | Teste | Situação |
| :--: | :-- | :-- | :--: |
| R-A1 | Item 9 do PHQ-9 ≥ 1 → N3 CRISE | `test_tu04_caso1_item9_precedencia`; `test_tu04_ra1_prevalece_sobre_todas`; `test_perfil_d` | Coberta |
| R-A2 | PHQ-9 ≥ 20 ou GAD-7 ≥ 15 → N2 | `test_tu04_caso2_phq9_grave`; `test_tu04_caso3_gad7_grave`; `test_perfil_c` | Coberta |
| R-A3 | PHQ-9 ≥ 10 ou GAD-7 ≥ 10 → N1 | `test_tu04_caso4` a `caso6`; `test_perfil_b` | Coberta |
| R-A4 | Nenhuma anterior → N0 | `test_tu04_caso7`; `test_tu04_caso8`; `test_perfil_a`; `test_perfil_e` | Coberta |

Pontuação e faixas (TU-01 a TU-03) também têm testes nos valores-limite. **4 de 4.**

## R-S: seleção de conteúdo (Quadro 20)

Código em `backend/app/rules/selecao.py`; testes `test_tu06_*` em `backend/tests/test_rules_checkin.py` (3 testes).

| Regra | Descrição no Quadro 20 | O que existe | Situação |
| :--: | :-- | :-- | :--: |
| R-S1 | Ordem de prioridade das tags ao buscar materiais | O código percorre `ORDEM_TAGS`, mas nenhum teste de `selecionar_materiais` usa duas ou mais tags para provar a ordem. (`test_thresholds` verifica a ordem das tags de `avaliar_checkin`, que é outra função.) | **Sem teste** |
| R-S2 | Escolher o material recomendado há mais tempo; nunca recomendado vem primeiro; empate pelo menor id | O código **exclui** materiais exibidos recentemente (`ids_exibidos_recentemente`); `test_tu06_rs2_ignora_ultimas_exibicoes` testa essa exclusão. Comportamento diferente do Quadro. | **Teste diverge** |
| R-S3 | Um material não aparece duas vezes na mesma resposta | A deduplicação existe no código (`adicionados`), mas nenhum teste a exercita. `test_tu06_rs3_match_exato_de_tags` testa outra coisa (casamento exato da tag). O código também usa o rótulo "R-S3" para o casamento de tags. | **Sem teste** |
| R-S4 | No máximo 3 materiais (2 para N2); excedentes descartados por prioridade | Os testes com `limite = 0` e `limite = 1` exercitam o mecanismo do limite, mas nenhum verifica o teto de 3 materiais, o de 2 para N2 nem o descarte das tags excedentes pela ordem de prioridade. | **Teste insuficiente** |
| R-S5 | Cada recomendação guarda a regra de origem (ex.: R-D4) e o motivo | `Sugestao` guarda "R-S3" ou "R-S6", não a regra de origem R-Dx. Não há teste. | **Sem teste** |
| R-S6 | Sem material para nenhuma tag, exibir apenas a orientação do nível | O código completa a lista com materiais BEM_ESTAR ou sem tag ("fallback"); `test_tu06_rs2_ignora_ultimas_exibicoes` verifica esse fallback. Comportamento diferente do Quadro. | **Teste diverge** |

**0 de 6 aderentes ao Quadro** (2 com teste divergente, 1 com teste insuficiente, 3 sem teste).

## Totais

| Tabela | Linhas | Cobertas (aderentes) | Cobertura |
| :-- | :--: | :--: | :--: |
| R-D | 6 | 6 | 100% |
| R-A | 4 | 4 | 100% |
| R-S | 6 | 0 | 0% |
| **Total (M1)** | **16** | **10** | **62,5%** |

## Ações para chegar a 100%

1. **PO decide** as divergências de R-S2, R-S5 e R-S6 (atualizar o Quadro 20 em nova versão da Visão ou ajustar o código). Os documentos são a fonte da verdade; enquanto não houver decisão, não se altera o código nem o teste. Registrado como [DEF-02](defeitos.md#def-02).
2. Escrever os testes que faltam para R-S1, R-S3 e R-S4 (nada disso depende de decisão do PO): [DEF-03](defeitos.md#def-03).
3. Reconferir a matriz na revisão da Sprint 4 e ao fim de cada sprint seguinte (Visão, Quadro 23: abaixo de 100%, criar o teste antes de novas funcionalidades).
