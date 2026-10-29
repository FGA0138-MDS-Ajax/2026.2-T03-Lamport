# Sintoniza

**Universidade de Brasília – Métodos de Desenvolvimento de Software – Turma 03 – Grupo Lamport**

O Sintoniza é uma aplicação web de apoio à saúde mental. Ela combina um **check-in diário**, uma **avaliação quinzenal** com instrumentos validados (PHQ-9 e GAD-7) e um **encaminhamento por regras explícitas** a conteúdos de fontes oficiais ou a serviços públicos de saúde, incluindo uma **Tela de Ajuda Imediata** para situações de risco.

!!! note "Nota de escopo"
    O Sintoniza é uma ferramenta de apoio e educação em saúde mental. O sistema não realiza diagnóstico clínico e não substitui avaliação ou tratamento profissional.

## Documentos

| Documento | Versão vigente | Data |
| :-- | :--: | :--: |
| [Visão do Produto e do Projeto](visao-produto-projeto.md) | 2.2 | 29/10/2026 |
| [Documento de Arquitetura](arquitetura.md) | 2.2 | 29/10/2026 |

Esta documentação publica sempre a versão mais recente de cada documento. As versões anteriores e o que mudou em cada uma estão no [Histórico de versões](historico-versoes.md).

## Equipe

| Matrícula | Nome | Função |
| :--: | :-- | :-- |
| 251026239 | Martin Quadros de Melo | Product Owner |
| 251012322 | Luiz Felipe Mendes Cordeiro Gomes | Desenvolvedor backend |
| 231026803 | Carlos Eduardo Pereira Alexandre | Desenvolvedor backend |
| 251010927 | Júlio Barros de Oliveira | Desenvolvedor frontend |
| 251040022 | Danilo Menezes Gomez | Desenvolvedor frontend |
| 251035784 | Vinícius Evangelista Borges Pinto | UX/UI, conteúdo e documentação |
| 251035274 | Hugo Sousa Rosa | Infraestrutura e qualidade |

## Cronograma

| Sprint | Entrega | Início | Fim |
| :--: | :-- | :--: | :--: |
| 1 | Definição do produto | 15/09/2026 | 30/09/2026 |
| 2 | Base do MVP | 01/10/2026 | 14/10/2026 |
| 3 | Regras e catálogo | 15/10/2026 | 28/10/2026 |
| 4 | Check-in diário | 29/10/2026 | 11/11/2026 |
| 5 | Avaliação e histórico | 12/11/2026 | 25/11/2026 |
| 6 | Qualidade e entrega | 26/11/2026 | 09/12/2026 |

Os entregáveis e o percentual de conclusão de cada sprint estão na [seção 2.3 da Visão](visao-produto-projeto.md#23-planejamento-das-fases-eou-iteracoes-do-projeto).

## Pilha tecnológica

React 18 + TypeScript + Vite no frontend; Python 3.12 + FastAPI + Pydantic v2 no backend; PostgreSQL 16 com SQLAlchemy 2 e Alembic; Argon2id e JWT para segurança; pytest e httpx para testes; Docker Compose para execução local; GitHub Actions para integração contínua.
