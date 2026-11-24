
import type { Nivel } from './checkins'
import { mockAvaliacoesApi } from '../mocks/avaliacoes'

export interface CreateAvaliacaoData {
  phq9: number[]
  gad7: number[]
}

export type Faixa =
  | 'MINIMA'
  | 'LEVE'
  | 'MODERADA'
  | 'MODERADAMENTE_GRAVE'
  | 'GRAVE'

export interface Recomendacao {
  titulo: string
  fonte: string
  resumo: string
  url: string
  regra: string
  motivo: string
}

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

export interface Avaliacao extends ResultadoAvaliacao {
  id: string
  criado_em: string
  respostas_phq9: number[]
  respostas_gad7: number[]
}

export const avaliacoesApi = {
  createAvaliacao: async (
    _token: string,
    data: CreateAvaliacaoData,
  ): Promise<Avaliacao> => mockAvaliacoesApi.createAvaliacao(data),

  listAvaliacoes: async (
    _token: string,
  ): Promise<AvaliacaoListItem[]> => mockAvaliacoesApi.listAvaliacoes(),

  getAvaliacao: async (
    _token: string,
    id: string,
  ): Promise<Avaliacao> => mockAvaliacoesApi.getAvaliacao(id),
}
