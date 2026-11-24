
import type {
  Avaliacao,
  AvaliacaoListItem,
  CreateAvaliacaoData,
} from '../api/avaliacoes'

const mockAvaliacoes: Avaliacao[] = [
  {
    id: '1',
    criado_em: '2026-11-20T10:30:00.000Z',
    respostas_phq9: [1, 0, 1, 0, 0, 1, 0, 0, 0],
    respostas_gad7: [1, 0, 1, 0, 1, 0, 1],
    escore_phq9: 3,
    escore_gad7: 4,
    faixa_phq9: 'MINIMA',
    faixa_gad7: 'MINIMA',
    nivel: 'autocuidado',
    orientacao:
      'Continue cuidando do seu bem-estar. Mantenha hábitos saudáveis e procure atividades que contribuam para sua qualidade de vida.',
    recomendacoes: [
      {
        titulo: 'Cuidados com a saúde mental',
        fonte: 'Ministério da Saúde',
        resumo:
          'Informações sobre práticas de autocuidado e manutenção da saúde mental.',
        url: 'https://www.gov.br/saude',
        regra: 'R01',
        motivo: 'Material informativo para promoção do autocuidado.',
      },
    ],
  },
  {
    id: '2',
    criado_em: '2026-11-15T14:00:00.000Z',
    respostas_phq9: [1, 1, 1, 1, 1, 1, 1, 1, 0],
    respostas_gad7: [1, 1, 1, 1, 1, 2, 1],
    escore_phq9: 8,
    escore_gad7: 9,
    faixa_phq9: 'LEVE',
    faixa_gad7: 'LEVE',
    nivel: 'atencao',
    orientacao:
      'Seus resultados indicam alguns sinais de sofrimento emocional. Observe como você tem se sentido e considere buscar orientação profissional.',
    recomendacoes: [
      {
        titulo: 'Saúde mental e qualidade de vida',
        fonte: 'Ministério da Saúde',
        resumo:
          'Conteúdo informativo sobre saúde mental, prevenção e busca por ajuda.',
        url: 'https://www.gov.br/saude',
        regra: 'R02',
        motivo: 'Material recomendado para resultados na faixa leve.',
      },
    ],
  },
  {
    id: '3',
    criado_em: '2026-11-10T09:15:00.000Z',
    respostas_phq9: [2, 2, 2, 2, 2, 2, 2, 1, 1],
    respostas_gad7: [2, 2, 2, 2, 2, 2, 3],
    escore_phq9: 16,
    escore_gad7: 15,
    faixa_phq9: 'MODERADAMENTE_GRAVE',
    faixa_gad7: 'MODERADA',
    nivel: 'prioritario',
    orientacao:
      'Seus resultados indicam sofrimento emocional significativo. É importante procurar acompanhamento de um profissional de saúde.',
    recomendacoes: [
      {
        titulo: 'Como buscar ajuda em saúde mental',
        fonte: 'Ministério da Saúde',
        resumo:
          'Orientações sobre os serviços de saúde disponíveis e como procurar atendimento.',
        url: 'https://www.gov.br/saude',
        regra: 'R03',
        motivo:
          'Material recomendado para resultados que exigem atenção profissional.',
      },
    ],
  },
]

export const mockAvaliacoesApi = {
  createAvaliacao: async (
    data: CreateAvaliacaoData,
  ): Promise<Avaliacao> => {
    const avaliacao: Avaliacao = {
      ...mockAvaliacoes[0],
      id: crypto.randomUUID(),
      criado_em: new Date().toISOString(),
      respostas_phq9: [...data.phq9],
      respostas_gad7: [...data.gad7],
      escore_phq9: data.phq9.reduce((total, resposta) => total + resposta, 0),
      escore_gad7: data.gad7.reduce((total, resposta) => total + resposta, 0),
    }

    mockAvaliacoes.unshift(avaliacao)

    return avaliacao
  },

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
