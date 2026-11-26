# Matriz regra × teste (M1)

Posição em **25/11/2026** (Sprint 5), `main` no commit `22bf6a4` (PR #80), com o mesmo conteúdo da `developer` em `0dca653`. O oráculo são os Quadros 16, 18 e 20 da Visão v2.7. Cada linha das tabelas de regras deve ter ao menos um teste que verifique o comportamento do Quadro (Visão, seção 6.1).

**Resultado: 16 de 16 linhas cobertas, M1 = 100%** (valor esperado: 100%). Na Sprint 4 eram 12 de 16 (75%); as quatro linhas que faltavam (R-S1, R-S2, R-S5 e R-S6) passaram a aderir ao Quadro 20 com o PR #66 (issues #46 e #47). Pela leitura literal da fórmula, o valor é o mesmo.

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
| R-A2 | PHQ-9 ≥ 20 ou GAD-7 ≥ 15 → N2 | `test_tu04_caso2_phq9_grave`; `test_tu04_caso3_gad7_grave`; `test_perfil_c`; TI-06 (perfil C, pela API) | Coberta |
| R-A3 | PHQ-9 ≥ 10 ou GAD-7 ≥ 10 → N1 | `test_tu04_caso4` a `caso6`; `test_perfil_b` | Coberta |
| R-A4 | Nenhuma anterior → N0 | `test_tu04_caso7`; `test_tu04_caso8`; `test_perfil_a`; `test_perfil_e` | Coberta |

Pontuação e faixas (TU-01 a TU-03) também têm testes nos valores-limite. **4 de 4.**

## R-S: seleção de conteúdo (Quadro 20)

Código em `backend/app/rules/selecao.py`; testes `test_tu06_*` em `backend/tests/test_rules_checkin.py` (9 testes), com o catálogo fixo `catalogo_tu06` (2 materiais por tag, 1 inativo). R-S2 e R-S5 também são verificadas na integração (`test_checkins.py` e `test_avaliacoes.py`).

| Regra | Descrição no Quadro 20 | Teste | Situação |
| :--: | :-- | :-- | :--: |
| R-S1 | Buscar os materiais ativos de cada tag na ordem AJUDA_PROFISSIONAL → ANSIEDADE → HUMOR → ESTRESSE → SONO → BEM_ESTAR | `test_tu06_rs1_ordem_prioridade_com_ajuda_profissional` (catálogo em ordem inversa, as seis tags); `test_tu06_rs1_material_inativo_nunca_sugerido` | Coberta |
| R-S2 | Escolher o material recomendado há mais tempo; nunca recomendado vem primeiro; empate pelo menor id | `test_tu06_rs2_nunca_recomendado_depois_mais_antigo_e_desempate_menor_id`; `test_tu06_rs2_rs4_um_material_por_tag_com_multiplos_ativos`; na integração, `test_rs2_checkin_uses_ultimas_exibicoes_from_database` e `test_rs2_avaliacao_rotaciona_materiais_com_ultimas_exibicoes` | Coberta |
| R-S3 | Um material não aparece duas vezes na mesma resposta | `test_tu06_rs3_material_com_duas_tags_aparece_uma_vez` | Coberta |
| R-S4 | No máximo 3 materiais (2 para N2); excedentes descartados por prioridade | `test_tu06_rs4_limite_tres_padrao_e_limite_dois_n2`; TI-06, perfil C (no máximo 2, de AJUDA_PROFISSIONAL) | Coberta |
| R-S5 | Cada recomendação guarda a regra de origem (ex.: R-D4) e o motivo | `test_tu06_rs5_checkin_preserva_regra_e_motivo_quadro_16` (R-D2 a R-D6); `test_tu06_rs5_avaliacao_preserva_regra_e_motivo_quadro_18` (R-A2 a R-A4); TI-03 e TI-06 conferem regra e motivo gravados no banco | Coberta |
| R-S6 | Sem material para nenhuma tag, exibir apenas a orientação do nível | `test_tu06_rs6_sem_material_disponivel_retorna_vazio_sem_fallback` | Coberta |

**6 de 6 aderentes ao Quadro.** As divergências do DEF-02 foram corrigidas no código: R-S1 usa a ordem completa (a mesma de `app/rules/avaliacao.py`) e descarta inativos; R-S2 ordena pela última exibição, sem janela de bloqueio; R-S5 grava a regra de origem; R-S6 não completa a lista com outros materiais.

## Totais

| Tabela | Linhas | Cobertas (aderentes) | Cobertura |
| :-- | :--: | :--: | :--: |
| R-D | 6 | 6 | 100% |
| R-A | 4 | 4 | 100% |
| R-S | 6 | 6 | 100% |
| **Total (M1)** | **16** | **16** | **100%** |

## Evolução

| Sprint | R-D | R-A | R-S | M1 |
| :--: | :--: | :--: | :--: | :--: |
| 3 | 0/6 | 0/4 | 0/6 | 0% |
| 4 | 6/6 | 4/4 | 2/6 | 75% |
| 5 | 6/6 | 4/4 | 6/6 | **100%** |

## Para manter em 100%

1. Reconferir a matriz sempre que `backend/app/rules/` ou os testes de regras mudarem, e na revisão de cada sprint.
2. Qualquer mudança nos Quadros 16, 18 ou 20 entra primeiro em nova versão da Visão; o teste muda junto com o código, no mesmo PR.
3. Ponto para o PO, sem efeito em M1: com um material por tag (R-S2), o teto de 2 do N2 (R-S4) nunca é atingido, porque o N2 só tem a tag AJUDA_PROFISSIONAL. Ver [Conferência dos PRs da Sprint 5](conferencia-prs-sprint-5.md#46-e-47-pr-66-selecao-de-conteudo-conforme-o-quadro-20).
