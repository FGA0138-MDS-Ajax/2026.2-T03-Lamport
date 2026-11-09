import { request } from './client'

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

// O backend devolve as tags em minúsculas ("humor", "bem_estar"); o frontend usa maiúsculas.
function normalizeCheckin(checkin: Checkin): Checkin {
  return { ...checkin, tags: (checkin.tags ?? []).map((tag) => tag.toUpperCase() as Tag) }
}

export const checkinsApi = {
  createCheckin: async (token: string, data: CreateCheckinData) =>
    normalizeCheckin(
      await request<Checkin>('/checkins', {
        method: 'POST',
        body: data,
        token,
      }),
    ),

  getTodayCheckin: async (token: string) =>
    normalizeCheckin(await request<Checkin>('/checkins/hoje', { token })),

  listCheckins: async (token: string, limite = 30) =>
    (await request<Checkin[]>(`/checkins?limite=${limite}`, { token })).map(normalizeCheckin),

  getCheckin: async (token: string, id: string) =>
    normalizeCheckin(await request<Checkin>(`/checkins/${encodeURIComponent(id)}`, { token })),
}
