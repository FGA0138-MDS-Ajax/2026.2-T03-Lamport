import type {
  Avaliacao,
  AvaliacaoListItem,
} from '../api/avaliacoes'

const mockAvaliacoes: Avaliacao[] = [
  {
    id: '1',
    criado_em: '2026-11-20T10:30:00.000Z',
    respostas_phq9: [1, 0, 1, 0, 0, 1, 0, 0, 0],
    respostas_gad7: [1, 0, 1, 0, 1, 0, 1],
    escore_phq9: 3,
    escore_gad7: 4,
    faixa_phq9: 'minima',
    faixa_gad7: 'minima',
    nivel: 'autocuidado',
    orientacao:
      'Continue acompanhando como você está. Seguem materiais de autocuidado.',
    recomendacoes: [
      {
        titulo: 'Saúde Mental – Saúde de A a Z',
        fonte: 'Ministério da Saúde',
        resumo: 'Explica o que é saúde mental.',
        url: 'https://www.gov.br/saude/saude-mental',
        regra: 'R-A4',
        motivo:
          'Suas respostas não indicaram sintomas marcantes nas últimas duas semanas.',
      },
    ],
  },
  {
    id: '2',
    criado_em: '2026-11-15T14:00:00.000Z',
    respostas_phq9: [1, 0, 1, 0, 0, 1, 0, 0, 0],
    respostas_gad7: [2, 2, 2, 1, 1, 1, 1],
    escore_phq9: 3,
    escore_gad7: 10,
    faixa_phq9: 'minima',
    faixa_gad7: 'moderada',
    nivel: 'atencao',
    orientacao:
      'Recomendamos conversar com um profissional de saúde. No SUS, a porta de entrada é a Unidade Básica de Saúde (UBS).',
    recomendacoes: [
      {
        titulo: 'Saúde Mental – Saúde de A a Z',
        fonte: 'Ministério da Saúde',
        resumo: 'Explica o que é saúde mental.',
        url: 'https://www.gov.br/saude/saude-mental',
        regra: 'R-A3',
        motivo:
          'Suas respostas indicam que conversar com um profissional de saúde pode ajudar.',
      },
      {
        titulo: 'Faça o que importa em tempos de estresse',
        fonte: 'OPAS/OMS',
        resumo: 'Guia ilustrado da OMS.',
        url: 'https://www.paho.org/pt/documentos/faca-que-importa',
        regra: 'R-A3',
        motivo:
          'Seu resultado no GAD-7 ficou na faixa moderada ou acima.',
      },
    ],
  },
  {
    id: '3',
    criado_em: '2026-11-10T09:15:00.000Z',
    respostas_phq9: [1, 0, 1, 0, 0, 1, 0, 0, 0],
    respostas_gad7: [3, 2, 2, 2, 2, 2, 2],
    escore_phq9: 3,
    escore_gad7: 15,
    faixa_phq9: 'minima',
    faixa_gad7: 'grave',
    nivel: 'prioritario',
    orientacao:
      'Suas respostas indicam sintomas intensos. Recomendamos procurar atendimento em saúde nos próximos dias, na sua UBS de referência ou em um CAPS. Se piorar, use a Ajuda Imediata.',
    recomendacoes: [
      {
        titulo: 'Saúde Mental – Saúde de A a Z',
        fonte: 'Ministério da Saúde',
        resumo: 'Explica o que é saúde mental.',
        url: 'https://www.gov.br/saude/saude-mental',
        regra: 'R-A2',
        motivo:
          'Suas respostas indicam sintomas intensos. Este material explica onde buscar atendimento.',
      },
    ],
  },
  {
    id: '4',
    criado_em: '2026-11-05T16:45:00.000Z',
    respostas_phq9: [0, 0, 0, 0, 0, 0, 0, 0, 1],
    respostas_gad7: [1, 0, 1, 0, 1, 0, 1],
    escore_phq9: 1,
    escore_gad7: 4,
    faixa_phq9: 'minima',
    faixa_gad7: 'minima',
    nivel: 'crise',
    orientacao: 'Procure a Tela de Ajuda Imediata para receber orientações.',
    recomendacoes: [],
  },
]

export const mockAvaliacoesApi = {
  listAvaliacoes: async (): Promise<AvaliacaoListItem[]> => {
    return mockAvaliacoes.map(
      ({
        id,
        criado_em,
        escore_phq9,
        escore_gad7,
        faixa_phq9,
        faixa_gad7,
        nivel,
      }) => ({
        id,
        criado_em,
        escore_phq9,
        escore_gad7,
        faixa_phq9,
        faixa_gad7,
        nivel,
      }),
    )
  },

  getAvaliacao: async (id: string): Promise<Avaliacao> => {
    const avaliacao = mockAvaliacoes.find((item) => item.id === id)

    if (!avaliacao) {
      throw new Error('Avaliação não encontrada')
    }

    return avaliacao
  },
}
