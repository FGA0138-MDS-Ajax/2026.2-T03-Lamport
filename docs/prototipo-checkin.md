# Protótipo do check-in e do histórico

**Versão 1.0 – 29/10/2026** · Telas do check-in diário, do resultado, da Tela de Ajuda Imediata e do histórico, em mobile e desktop.

!!! warning "Aguardando validação do frontend"
    Este documento atende à issue [#2](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/issues/2) e segue a [Visão do Produto e do Projeto](visao-produto-projeto.md) e o [Documento de Arquitetura](arquitetura.md), ambos na versão 2.2, e o [Vocabulário do check-in](vocabulario-checkin.md) v1.1. **Onde houver divergência, valem a Visão e a Arquitetura.** Pelos critérios de aceite da issue, o frontend valida o protótipo antes da implementação.

| | |
| :-- | :-- |
| **Projeto** | Sintoniza – Grupo Lamport, MDS 2026.2, Turma 03 (UnB) |
| **Issue** | [#2](https://github.com/FGA0138-MDS-Ajax/2026.2-T03-Lamport/issues/2) [UX] Protótipo das telas de check-in diário e histórico |
| **Base** | Visão do Produto e do Projeto v2.2 e Documento de Arquitetura v2.2, ambos de 29/10/2026; Vocabulário do check-in v1.1 |
| **Figma** | [Arquivo de design](https://www.figma.com/design/eY40HsGcHOBxnHPRMeB9gj) · [Protótipo navegável (mobile)](https://www.figma.com/proto/eY40HsGcHOBxnHPRMeB9gj?node-id=1-2&starting-point-node-id=1%3A2) |
| **Elaboração** | Vinícius Evangelista Borges Pinto (UX/UI, conteúdo e documentação) |
| **Validação** | Júlio Barros de Oliveira e Danilo Menezes Gomez (frontend) – pendente |

## Histórico de revisões

| Data | Versão | Descrição | Autor |
| :--: | :--: | :-- | :-- |
| 29/10/2026 | 1.0 | Protótipo alinhado à Visão v2.2 e ao vocabulário v1.1: 20 telas mobile navegáveis e 10 telas desktop de referência. | Vinícius E. B. Pinto |

---

## 1 Objetivo e escopo

Este documento registra o protótipo das telas do check-in diário (C02/R05 e C02/R06), da Tela de Ajuda Imediata (C04/R10 e C04/R11) e do histórico de check-ins (C05/R12). O protótipo fica no Figma; aqui estão o fluxo de navegação, a correspondência com as tarefas da issue #2 e a imagem de cada tela.

O mobile, com 390 px de largura, é a referência principal e o único com navegação no Figma. O desktop mostra as telas principais em 1280 px, sem navegação.

Os textos seguem a Visão e, no que ela não define, o vocabulário do check-in. As exceções são “Olá!”, o e-mail do usuário e “Sair”, que já existem no frontend atual, e “Início” e “Histórico”, que são os nomes das páginas no menu.

Ficam fora do escopo a avaliação quinzenal (C03), as avaliações no histórico (parte do R12 prevista para a Sprint 5), o cadastro, o login e a página de termos de uso.

!!! note "Como navegar no protótipo"
    O [protótipo navegável](https://www.figma.com/proto/eY40HsGcHOBxnHPRMeB9gj?node-id=1-2&starting-point-node-id=1%3A2) abre no fluxo “Check-in diário (mobile)”, que começa na tela M-01a. O fluxo “Histórico (mobile)” começa na M-06a. No modo de desenvolvimento (Dev Mode) do Figma, as anotações trazem detalhes de implementação, como os links `tel:188` e `tel:192` e o estilo de foco.

## 2 Fluxo

A Figura 1 mostra o caminho principal do check-in no protótipo mobile. Ele segue a Figura 3 da Arquitetura e o fluxo de duas etapas do vocabulário (seção 6).

**Figura 1 – Fluxo do protótipo mobile**

```mermaid
flowchart TB
    A["M-01a · Início"] -- "Fazer check-in" --> B["M-02a / M-02b · Etapa 1<br/>P1 a P4, opcionais"]
    B -- "Continuar" --> C["M-03a · Etapa 2<br/>P5, obrigatória"]
    C -- "Concluir sem resposta" --> V["M-03b · Erro de validação"]
    C -- "Marca Não" --> N["M-03e · Não marcado"]
    C -- "Marca Sim" --> S["M-03f · Sim marcado"]
    N -- "Concluir check-in" --> E["M-03c · Enviando…"]
    E --> R["M-04a · Conteúdos do dia"]
    S -- "Concluir check-in" --> H["M-05a · Tela de Ajuda Imediata"]
    R -- "Voltar ao início" --> F["M-01b · Check-in já feito"]
    F -- "Ver check-in de hoje" --> R
    T["Qualquer tela"] -- "Preciso de ajuda agora" --> G["M-05c · Tela de Ajuda Imediata"]
    style H fill:#f8d7da,stroke:#c0392b,color:#1f2a2e
    style G fill:#f8d7da,stroke:#c0392b,color:#1f2a2e
```

Fora do caminho principal, o protótipo mostra também:

- o erro de conexão ao enviar, que mantém as respostas (M-03d);
- o resultado sem materiais (M-04c);
- a falha ao salvar um check-in com P5 = Sim (M-05b);
- o histórico vazio, carregando e com erro (M-06b a M-06d);
- o menu aberto (M-01c).

Em todas as telas, o logo “Sintoniza” leva ao início e o ☰ abre o menu.

## 3 Rastreabilidade

**Quadro 1 – Tarefas da issue #2 e telas do protótipo**

| Tarefa da issue #2 | Requisito ou referência | Telas |
| :-- | :-- | :-- |
| Check-in: perguntas P1 a P5 com os textos e as opções do Quadro 15 da Visão; P1 a P4 opcionais e P5 obrigatória | C02/R05; Visão, Quadro 15 | M-02a, M-02b, M-03a a M-03f |
| Estado “check-in de hoje já feito”, com o resultado do dia | Arquitetura, Figura 3 | M-01b, que leva à M-04a |
| Resultado sem risco: até 3 materiais com título, fonte, resumo, link e motivo | C02/R06; Visão, Quadro 16 | M-04a, M-04c |
| Resultado com P5 = Sim: Tela de Ajuda Imediata, sem materiais | C04/R10; Visão, seção 4.5.5 | M-03f, que leva à M-05a; M-05b |
| Botão “Preciso de ajuda agora” em todas as telas | C04/R11 | Todas; o botão abre a M-05c |
| Histórico: últimos 30 check-ins com data, humor e tags | C05/R12 | M-06a a M-06d |

**Quadro 2 – Critérios de aceite da issue #2**

| Critério | Como foi atendido |
| :-- | :-- |
| Link do Figma anexado na issue | Links do arquivo e do protótipo navegável no início deste documento, para comentar na issue. |
| Textos iguais aos da Visão e, no que ela não define, aos do vocabulário revisado pelo PO (#3) | Atendido, com as exceções da seção 1, que já existem no frontend atual ou são nomes de páginas. |
| O frontend validou o protótipo antes da implementação | Pendente. |

## 4 Decisões de interface aplicadas

O protótipo aplica as decisões do vocabulário (seção 7) e os requisitos de acessibilidade da seção 6.8:

- **P1 a P4 opcionais (D3, aprovada na v2.2):** “Prefiro não responder” é a última opção de cada pergunta e “Continuar” fica sempre habilitado.
- **Histórico sem a P5 e sem o nível (D6):** cada item mostra apenas a data, o humor e os temas.
- **Sem ícones nas opções (D7):** toda opção tem rótulo em texto. O ♥ do botão “Preciso de ajuda agora” é decorativo.
- **Aviso de que o check-in não é teste de saúde (D8):** aparece no resultado (M-04a e M-04c).
- **Tela de Ajuda imediata com P5 = Sim (D9):** a tela abre ao concluir, sem depender do envio. Se o envio falhar, os contatos continuam visíveis (M-05b). A D9 ainda aguarda decisão do PO (vocabulário, seção 10, ponto 4).
- **Acessibilidade:**
    - as escalas aparecem em lista vertical no mobile, na ordem do Quadro 4 do vocabulário, e as opções têm 47 px de altura;
    - a opção marcada tem o ponto no círculo e o texto em negrito, e não só a cor;
    - a M-02b mostra o foco do teclado com contorno de 3 px na cor primária, a 2 px da opção, como o `:focus-visible` do `styles.css`;
    - os nomes das camadas indicam o papel de cada elemento, como “h1 (recebe o foco)”, “descrição (aria-describedby)” e “Registro (role=status)”.

As respostas da M-02b (humor ruim, bastante ansiedade, sono ruim e P4 sem resposta) geram exatamente os temas da M-04a e o item “Hoje” da M-06a: Ansiedade, Humor e Sono, na ordem da regra R-S1.

## 5 Telas mobile (390 px)

Clique em uma imagem para abri-la em tamanho real.

### 5.1 Início e menu

- **M-01a:** início sem check-in no dia, com o cartão “Check-in de hoje” (vocabulário, Quadro 7).
- **M-01b:** início com o check-in do dia feito. O botão “Ver check-in de hoje” mostra o resultado já registrado.
- **M-01c:** menu aberto pelo ☰, com Início, Histórico, o e-mail e “Sair”.

**Figura 2 – Início e menu**

[![M-01a – Início sem check-in no dia](prototipo/m-01a.png){ width="220" loading=lazy }](prototipo/m-01a.png)
[![M-01b – Início com o check-in do dia feito](prototipo/m-01b.png){ width="220" loading=lazy }](prototipo/m-01b.png)
[![M-01c – Menu aberto](prototipo/m-01c.png){ width="220" loading=lazy }](prototipo/m-01c.png)

### 5.2 Etapa 1: P1 a P4

- **M-02a:** etapa vazia, sem opção pré-selecionada.
- **M-02b:** etapa respondida, com a P4 sem resposta e o foco do teclado na primeira opção dela.

**Figura 3 – Etapa 1 do check-in**

[![M-02a – Etapa 1 vazia](prototipo/m-02a.png){ width="220" loading=lazy }](prototipo/m-02a.png)
[![M-02b – Etapa 1 respondida, com foco visível](prototipo/m-02b.png){ width="220" loading=lazy }](prototipo/m-02b.png)

### 5.3 Etapa 2: P5

- **M-03a:** etapa vazia.
- **M-03e e M-03f:** “Não” e “Sim” marcados. Marcar uma opção não envia o check-in; o envio só acontece em “Concluir check-in”. Marcar “Sim” não pede confirmação (vocabulário, Quadro 9).
- **M-03b:** erro ao concluir sem responder.
- **M-03c:** envio em andamento, com o botão desabilitado.
- **M-03d:** erro de conexão, com as respostas mantidas.

**Figura 4 – Etapa 2 do check-in: resposta**

[![M-03a – Etapa 2 vazia](prototipo/m-03a.png){ width="220" loading=lazy }](prototipo/m-03a.png)
[![M-03e – Etapa 2 com Não marcado](prototipo/m-03e.png){ width="220" loading=lazy }](prototipo/m-03e.png)
[![M-03f – Etapa 2 com Sim marcado](prototipo/m-03f.png){ width="220" loading=lazy }](prototipo/m-03f.png)

**Figura 5 – Etapa 2 do check-in: erros e envio**

[![M-03b – Erro de validação](prototipo/m-03b.png){ width="220" loading=lazy }](prototipo/m-03b.png)
[![M-03c – Enviando](prototipo/m-03c.png){ width="220" loading=lazy }](prototipo/m-03c.png)
[![M-03d – Erro de conexão](prototipo/m-03d.png){ width="220" loading=lazy }](prototipo/m-03d.png)

### 5.4 Resultado

- **M-04a:** conteúdos do dia. São até 3 materiais, na ordem da regra R-S1, cada um com “Por que estou vendo isto?” e o motivo da regra (Visão, Quadro 16). Títulos, fontes e resumos estão como marcadores: os reais vêm do `materiais.yaml`.
- **M-04c:** resultado sem materiais (regra R-S6).

**Figura 6 – Resultado do check-in**

[![M-04a – Conteúdos do dia](prototipo/m-04a.png){ width="220" loading=lazy }](prototipo/m-04a.png)
[![M-04c – Resultado sem materiais](prototipo/m-04c.png){ width="220" loading=lazy }](prototipo/m-04c.png)

### 5.5 Tela de Ajuda Imediata

- **M-05a:** aberta pelo check-in com P5 = Sim. Tem o conteúdo fixo da seção 4.5.5 da Visão e os textos do Quadro 12 do vocabulário.
- **M-05b:** mesma tela, quando o check-in não pôde ser salvo.
- **M-05c:** aberta pelo botão “Preciso de ajuda agora”. Tem só o conteúdo fixo, sem os textos do check-in.

**Figura 7 – Tela de Ajuda Imediata**

[![M-05a – Tela de Ajuda aberta pelo check-in](prototipo/m-05a.png){ width="220" loading=lazy }](prototipo/m-05a.png)
[![M-05b – Tela de Ajuda com falha ao salvar](prototipo/m-05b.png){ width="220" loading=lazy }](prototipo/m-05b.png)
[![M-05c – Tela de Ajuda aberta pelo botão](prototipo/m-05c.png){ width="220" loading=lazy }](prototipo/m-05c.png)

### 5.6 Histórico

- **M-06a:** lista com data, humor e temas (vocabulário, Quadro 14).
- **M-06b a M-06d:** histórico vazio, carregando e com erro.

**Figura 8 – Histórico de check-ins**

[![M-06a – Histórico](prototipo/m-06a.png){ width="220" loading=lazy }](prototipo/m-06a.png)
[![M-06b – Histórico vazio](prototipo/m-06b.png){ width="220" loading=lazy }](prototipo/m-06b.png)
[![M-06c – Histórico carregando](prototipo/m-06c.png){ width="220" loading=lazy }](prototipo/m-06c.png)
[![M-06d – Histórico com erro](prototipo/m-06d.png){ width="220" loading=lazy }](prototipo/m-06d.png)

## 6 Telas desktop (1280 px)

O desktop repete os textos das telas principais do mobile, com o cabeçalho do frontend atual: Início, Histórico, o e-mail, “Sair” e o botão “Preciso de ajuda agora”. É uma referência visual estática; a navegação está só no protótipo mobile.

**Quadro 3 – Telas desktop e equivalentes no mobile**

| Tela | Estado | Mobile |
| :--: | :-- | :--: |
| [D-01a](prototipo/d-01a.png) | Início sem check-in no dia | M-01a |
| [D-01b](prototipo/d-01b.png) | Início com o check-in do dia feito | M-01b |
| [D-02b](prototipo/d-02b.png) | Etapa 1 respondida, com foco visível | M-02b |
| [D-03a](prototipo/d-03a.png) | Etapa 2 vazia | M-03a |
| [D-03b](prototipo/d-03b.png) | Etapa 2 com erro de validação | M-03b |
| [D-04a](prototipo/d-04a.png) | Conteúdos do dia | M-04a |
| [D-05a](prototipo/d-05a.png) | Tela de Ajuda aberta pelo check-in | M-05a |
| [D-05c](prototipo/d-05c.png) | Tela de Ajuda aberta pelo botão | M-05c |
| [D-06a](prototipo/d-06a.png) | Histórico | M-06a |
| [D-06b](prototipo/d-06b.png) | Histórico vazio | M-06b |

??? example "Figura 9 – Telas desktop"
    ![D-01a – Início sem check-in no dia](prototipo/d-01a.png){ loading=lazy }

    ![D-01b – Início com o check-in do dia feito](prototipo/d-01b.png){ loading=lazy }

    ![D-02b – Etapa 1 respondida, com foco visível](prototipo/d-02b.png){ loading=lazy }

    ![D-03a – Etapa 2 vazia](prototipo/d-03a.png){ loading=lazy }

    ![D-03b – Etapa 2 com erro de validação](prototipo/d-03b.png){ loading=lazy }

    ![D-04a – Conteúdos do dia](prototipo/d-04a.png){ loading=lazy }

    ![D-05a – Tela de Ajuda aberta pelo check-in](prototipo/d-05a.png){ loading=lazy }

    ![D-05c – Tela de Ajuda aberta pelo botão](prototipo/d-05c.png){ loading=lazy }

    ![D-06a – Histórico](prototipo/d-06a.png){ loading=lazy }

    ![D-06b – Histórico vazio](prototipo/d-06b.png){ loading=lazy }

## 7 Pendências

O protótipo segue o texto atual dos documentos. Quatro pontos do vocabulário (seção 10) ainda aguardam decisão do PO e podem mudar as telas:

- **Ponto 2:** check-in com P1 a P4 em branco recebe o tema Bem-estar, que hoje aparece com o motivo “Você não indicou dificuldades marcantes hoje.”
- **Ponto 4:** momento em que a Tela de Ajuda abre (decisão D9, já aplicada no protótipo).
- **Ponto 6:** escalas em sentidos opostos. P1 e P3 vão de “Muito ruim” a “Muito bom”; P2 e P4 vão de “Nada” a “Extremamente”.
- **Ponto 7:** a P4 pergunta sobre sobrecarga, mas gera o tema exibido como “Estresse”.
