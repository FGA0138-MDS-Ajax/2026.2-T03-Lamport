# Histórico de versões

Esta página registra todas as versões dos documentos do projeto. **A versão mais recente de cada documento é a que vale**; as anteriores ficam aqui apenas como registro da evolução.

## Visão do Produto e do Projeto

| Data | Versão | Descrição | Autor |
| :--: | :--: | :-- | :-- |
| 30/09/2026 | 1.0 | Atualização do nome do produto para Sintoniza e definição das responsabilidades iniciais da equipe. | Equipe do projeto |
| 15/10/2026 | 2.0 | Reformulação após o feedback da apresentação: fluxo principal especificado (check-in diário, avaliação quinzenal com PHQ-9 e GAD-7, tabela de decisão, regras de seleção e catálogo curado de fontes oficiais); redução de escopo (remoção dos perfis Administrador e Curador, de lembretes e de IA); estratégia e roteiro de testes detalhados, incluindo testes de vazamento de dados; GQM revisado; replanejamento das sprints 3 a 6. | Grupo Lamport |
| 18/10/2026 | **2.1** (vigente) | Revisão de escopo para manter apenas compromissos essenciais: remoção dos requisitos não funcionais de interface responsiva, execução com Docker Compose, publicação em nuvem e verificação automática de links; remoção das metas de usabilidade, desempenho, capacidade e cobertura de código e dos testes associados; remoção dos itens Should e Could não essenciais; testes de segurança concentrados em cinco casos; requisitos e roteiro de testes renumerados. | Grupo Lamport |

### Principais mudanças entre versões

??? abstract "1.0 → 2.0"
    - **Produto:** de "app de saúde mental" genérico (React Native ou web) para **aplicação web** com dois formulários definidos: check-in diário (P1–P5) e avaliação quinzenal (PHQ-9 + GAD-7).
    - **Regras:** recomendação passa a ser uma tabela de decisão explícita (R-D, R-A, R-S) com valores-limite publicados, implementada como funções puras.
    - **Conteúdo:** catálogo curado de links oficiais (gov.br, OPAS/OMS, CVV) em arquivo versionado, sem API externa.
    - **Perfis:** removidos Administrador e Curador; ficam Visitante e Usuário.
    - **Equipe:** entrada de Júlio Barros de Oliveira (frontend).
    - **Backlog:** passa de 17 para 22 requisitos, com critérios de aceite e testes vinculados.
    - **Testes e GQM:** roteiro com TU, TI, TS, TSI e TNF; GQM com 13 métricas (M1–M13).
    - **Sprints 3 a 6 replanejadas:** regras e catálogo na Sprint 3; check-in na 4; avaliação e histórico na 5.

??? abstract "2.0 → 2.1"
    - **Requisitos removidos:** interface responsiva (R22), Docker Compose como requisito (R20), publicação em nuvem (R21), verificação automática de links (R16), avaliação de utilidade (R17), biblioteca de materiais (R18), gráfico de humor (R14), aviso de avaliação pendente (R10).
    - **Backlog renumerado:** 14 requisitos (R01–R14). O único Should é R07; não há itens Could.
    - **Catálogo:** mínimo de 1 material ativo por tag (antes: 2 por tag, 12 no total).
    - **Testes:** removidos TU-09, TU-10, TI-08, TS-06 a TS-09, TSI-06 e TNF-01 a TNF-03; segurança concentrada em TS-01 a TS-05.
    - **GQM:** reduzido a 5 métricas (M1–M5); sem metas de usabilidade, desempenho ou cobertura.
    - **Processo:** acompanhamento semanal; merge direto na `main` após CI e revisão; Definição de Pronto simplificada.
    - **Riscos:** removido o risco de hospedagem gratuita; riscos renumerados (R1–R9).

## Documento de Arquitetura

| Data | Versão | Descrição | Autor(es) |
| :--: | :--: | :-- | :-- |
| 05/10/2026 | 1.0 | Elaboração inicial do Documento de Arquitetura do Sintoniza, alinhada à Visão do Produto e do Projeto. | Grupo Lamport |
| 07/10/2026 | 1.1 | Revisão conforme feedback: critérios de indicador crítico, fluxo de segurança, cliente web em React, dependências dos pacotes, modelo de classes, visão de implantação e rastreabilidade. | Grupo Lamport |
| 15/10/2026 | 2.0 | Alinhamento à Visão v2.0: remoção dos perfis Administrador e Curador e do componente de administração; módulo de regras como funções puras com contrato documentado; catálogo versionado em arquivo com carga por seed; avaliação quinzenal PHQ-9/GAD-7; dois diagramas de atividades (check-in e avaliação); contrato da API; restrições de segurança verificáveis por testes; Docker Compose como implantação obrigatória. | Grupo Lamport |
| 18/10/2026 | **2.1** (vigente) | Alinhamento à Visão v2.1: remoção das metas de desempenho, capacidade e cobertura de código, da publicação em nuvem, do verificador automático de links, da auditoria de dependências e da avaliação de utilidade dos materiais; restrições de segurança limitadas ao que é verificado pelos testes TS-01 a TS-05; características de qualidade descritas sem metas numéricas. | Grupo Lamport |

### Principais mudanças entre versões

??? abstract "1.1 → 2.0"
    - Módulos `presentation / application / recommendation / content / infrastructure` substituídos por `api / security / services / rules / domain / persistence / catalog`.
    - Removidos EventoCritico, Consentimento, Conteúdo e AvaliaçãoRecomendação; entram CheckinDiario, Avaliacao, Material e Recomendacao. O nível CRISE fica registrado no próprio check-in ou avaliação.
    - A regra de risco "humor mínimo em três check-ins seguidos" saiu; o risco passa a ser indicado por P5 = Sim ou pelo item 9 do PHQ-9 ≥ 1.
    - Implantação muda de nuvem a definir para Docker Compose (web, api, db).
    - Inclusão do contrato das funções de regras (Quadro 5) e do contrato da API REST (Quadro 6).

??? abstract "2.0 → 2.1"
    - Removidas as metas de desempenho (p95 < 1000 ms), capacidade (50/20 usuários) e cobertura (rules ≥ 90%, backend ≥ 60%).
    - Removidos o verificador de links, o pip-audit/npm audit, as restrições CORS/logs como metas verificáveis e a rota `PATCH /api/recomendacoes/{id}`.
    - A CI passa a executar apenas os testes automatizados (pytest com PostgreSQL de teste).
    - Docker Compose deixa de ser requisito e vira forma de execução para desenvolvimento e demonstração.
    - Restrições de banco reduzidas a três: unicidade de (usuario_id, data), unicidade de e-mail e slug, e chaves estrangeiras com cascata.
