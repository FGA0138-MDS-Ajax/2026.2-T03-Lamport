import { request } from './client'
import type { Recomendacao } from './recomendacoes'

export interface CreateCheckinData {
  p1: number | null
  p2: number | null
  p3: number | null
  p4: number | null
  p5: boolean
}

export type Nivel = 'autocuidado' | 'atencao' | 'prioritario' | 'crise'

export type Tag = 'HUMOR' | 'ANSIEDADE' | 'SONO' | 'ESTRESSE' | 'BEM_ESTAR' | 'AJUDA_PROFISSIONAL'

export interface Checkin {
  id: string
  data: string
  p1: number | null
  p2: number | null
  p3: number | null
  p4: number | null
  p5: boolean
  nivel: Nivel
  tags: Tag[]
  criado_em: string
}

/** Resposta de `POST /api/checkins`: nível, tags e recomendações (Arquitetura, Quadro 6). */
export interface CheckinResultado {
  nivel: Nivel
  tags: Tag[]
  recomendacoes: Recomendacao[]
}

/** Resposta de `GET /api/checkins/hoje`: respostas do dia e as recomendações gravadas (DP-2). */
export interface CheckinHoje extends CheckinResultado {
  p1: number | null
  p2: number | null
  p3: number | null
  p4: number | null
  p5: boolean
}

// O backend devolve as tags em minúsculas ("humor", "bem_estar"); o frontend usa maiúsculas.
function normalizeCheckin<T extends { tags: Tag[] }>(checkin: T): T {
  return { ...checkin, tags: (checkin.tags ?? []).map((tag) => tag.toUpperCase() as Tag) }
}

function normalizeResultado<T extends CheckinResultado>(resultado: T): T {
  return normalizeCheckin({ ...resultado, recomendacoes: resultado.recomendacoes ?? [] })
}

export const checkinsApi = {
  createCheckin: async (token: string, data: CreateCheckinData) =>
    normalizeResultado(
      await request<CheckinResultado>('/checkins', {
        method: 'POST',
        body: data,
        token,
      }),
    ),

  getTodayCheckin: async (token: string) =>
    normalizeResultado(await request<CheckinHoje>('/checkins/hoje', { token })),

  listCheckins: async (token: string, limite = 30) =>
    (await request<Checkin[]>(`/checkins?limite=${limite}`, { token })).map(normalizeCheckin),

  getCheckin: async (token: string, id: string) =>
    normalizeCheckin(await request<Checkin>(`/checkins/${encodeURIComponent(id)}`, { token })),
}
