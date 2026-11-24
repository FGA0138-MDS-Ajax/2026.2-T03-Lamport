import type { Nivel } from './checkins'
import { request } from './client'
import { mockAvaliacoesApi } from '../mocks/avaliacoes'

export interface CreateAvaliacaoData {
  phq9: number[]
  gad7: number[]
}

export type Faixa =
  | 'minima'
  | 'leve'
  | 'moderada'
  | 'moderadamente_grave'
  | 'grave'

export interface Recomendacao {
  titulo: string
  fonte: string
  resumo: string
  url: string
  regra: string
  motivo: string
}

/**
 * Resultado retornado pelo POST /api/avaliacoes.
 * Corresponde ao schema AvaliacaoCreatedResponse do backend.
 */
export interface ResultadoAvaliacao {
  escore_phq9: number
  escore_gad7: number
  faixa_phq9: Faixa
  faixa_gad7: Faixa
  nivel: Nivel
  orientacao: string
  recomendacoes: Recomendacao[]
}

export interface AvaliacaoListItem {
  id: string
  criado_em: string
  escore_phq9: number
  escore_gad7: number
  faixa_phq9: Faixa
  faixa_gad7: Faixa
  nivel: Nivel
}

/**
 * Representação completa utilizada pelos mocks de consulta individual.
 */
export interface Avaliacao extends ResultadoAvaliacao {
  id: string
  criado_em: string
  respostas_phq9: number[]
  respostas_gad7: number[]
}

export const avaliacoesApi = {
  createAvaliacao: async (
    token: string,
    data: CreateAvaliacaoData,
  ): Promise<ResultadoAvaliacao> => {
    return request<ResultadoAvaliacao>('/avaliacoes', {
      method: 'POST',
      body: data,
      token,
    })
  },

  listAvaliacoes: async (
    _token: string,
  ): Promise<AvaliacaoListItem[]> => mockAvaliacoesApi.listAvaliacoes(),

  getAvaliacao: async (
    _token: string,
    id: string,
  ): Promise<Avaliacao> => mockAvaliacoesApi.getAvaliacao(id),
}
