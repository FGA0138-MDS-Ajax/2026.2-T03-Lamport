import type { Nivel } from './checkins'
import { request } from './client'

export interface CreateAvaliacaoData {
  phq9: number[]
  gad7: number[]
}

export type Faixa = 'minima' | 'leve' | 'moderada' | 'moderadamente_grave' | 'grave'

export interface Recomendacao {
  titulo: string
  fonte: string
  resumo: string
  url: string
  regra: string
  motivo: string
}

/**
 * Resposta de POST /api/avaliacoes e GET /api/avaliacoes/{id}.
 * Corresponde a AvaliacaoCreatedResponse do backend.
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

/**
 * Item retornado por GET /api/avaliacoes.
 * Corresponde a AvaliacaoItemResponse do backend.
 */
export interface AvaliacaoListItem {
  id: string
  data: string
  escore_phq9: number
  escore_gad7: number
  faixa_phq9: Faixa
  faixa_gad7: Faixa
  nivel: Nivel
}

/**
 * Tipo de compatibilidade para componentes que ainda utilizam
 * metadados da implementação anterior da Issue #58.
 *
 * Esses campos adicionais não são retornados pelo GET individual.
 */
export type Avaliacao = ResultadoAvaliacao

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

  listAvaliacoes: async (token: string): Promise<AvaliacaoListItem[]> => {
    return request<AvaliacaoListItem[]>('/avaliacoes', {
      method: 'GET',
      token,
    })
  },

  getAvaliacao: async (token: string, id: string): Promise<Avaliacao> => {
    return request<Avaliacao>(`/avaliacoes/${id}`, {
      method: 'GET',
      token,
    })
  },
}
