import type { Nivel } from './checkins'
import { request } from './client'
import type { Recomendacao } from './recomendacoes'

/**
 * Corpo de `POST /api/avaliacoes` (Arquitetura, Quadro 6).
 * `phq9`: 9 inteiros de 0 a 3; `gad7`: 7 inteiros de 0 a 3 (validado no backend).
 */
export interface CreateAvaliacaoData {
  phq9: number[]
  gad7: number[]
}

export type Faixa = 'minima' | 'leve' | 'moderada' | 'moderadamente_grave' | 'grave'

/**
 * Resposta de `POST /api/avaliacoes` e de `GET /api/avaliacoes/{id}` (mesmos campos, DP-3).
 * Corresponde a `AvaliacaoCreatedResponse` do backend.
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
 * Item de `GET /api/avaliacoes`.
 * Corresponde a `AvaliacaoItemResponse` do backend.
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

  getAvaliacao: async (token: string, id: string): Promise<ResultadoAvaliacao> => {
    return request<ResultadoAvaliacao>(`/avaliacoes/${id}`, {
      method: 'GET',
      token,
    })
  },
}
