import type { AvaliacaoListItem, ResultadoAvaliacao } from '../api/avaliacoes'
import { ApiError } from '../api/client'

interface MockAvaliacao {
  id: string
  data: string
  resultado: ResultadoAvaliacao
}

const mockAvaliacoes: MockAvaliacao[] = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    data: '2026-11-20',
    resultado: {
      escore_phq9: 3,
      escore_gad7: 4,
      faixa_phq9: 'minima',
      faixa_gad7: 'minima',
      nivel: 'autocuidado',
      orientacao: 'Continue acompanhando como você está. Seguem materiais de autocuidado.',
      recomendacoes: [
        {
          titulo: 'Saúde Mental – Saúde de A a Z',
          fonte: 'Ministério da Saúde',
          resumo: 'Explica o que é saúde mental.',
          url: 'https://www.gov.br/saude/saude-mental',
          regra: 'R-A4',
          motivo: 'Suas respostas não indicaram sintomas marcantes nas últimas duas semanas.',
        },
      ],
    },
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    data: '2026-11-15',
    resultado: {
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
          motivo: 'Suas respostas indicam que conversar com um profissional de saúde pode ajudar.',
        },
        {
          titulo: 'Faça o que importa em tempos de estresse',
          fonte: 'OPAS/OMS',
          resumo: 'Guia ilustrado da OMS.',
          url: 'https://www.paho.org/pt/documentos/faca-que-importa',
          regra: 'R-A3',
          motivo: 'Seu resultado no GAD-7 ficou na faixa moderada ou acima.',
        },
      ],
    },
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440003',
    data: '2026-11-10',
    resultado: {
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
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440004',
    data: '2026-11-05',
    resultado: {
      escore_phq9: 1,
      escore_gad7: 4,
      faixa_phq9: 'minima',
      faixa_gad7: 'minima',
      nivel: 'crise',
      orientacao: 'Tela de Ajuda Imediata. Nenhum material é exibido.',
      recomendacoes: [],
    },
  },
  {
    id: '4',
    data: '2026-11-05',
    resultado: {
      escore_phq9: 1,
      escore_gad7: 4,
      faixa_phq9: 'minima',
      faixa_gad7: 'minima',
      nivel: 'crise',
      orientacao: 'Procure a Tela de Ajuda Imediata para receber orientações.',
      recomendacoes: [],
    },
  },
]

export const mockAvaliacoesApi = {
  listAvaliacoes: async (): Promise<AvaliacaoListItem[]> => {
    return mockAvaliacoes.map(({ id, data, resultado }) => ({
      id,
      data,
      escore_phq9: resultado.escore_phq9,
      escore_gad7: resultado.escore_gad7,
      faixa_phq9: resultado.faixa_phq9,
      faixa_gad7: resultado.faixa_gad7,
      nivel: resultado.nivel,
    }))
  },

  getAvaliacao: async (id: string): Promise<ResultadoAvaliacao> => {
    const avaliacao = mockAvaliacoes.find((item) => item.id === id)

    if (!avaliacao) {
      throw new ApiError(404, 'Avaliacao not found')
    }

    return avaliacao.resultado
  },
}
