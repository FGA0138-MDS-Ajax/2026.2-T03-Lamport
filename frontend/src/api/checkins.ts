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

export const checkinsApi = {
  createCheckin: (token: string, data: CreateCheckinData) =>
    request<Checkin>('/checkins', {
      method: 'POST',
      body: data,
      token,
    }),

  getTodayCheckin: (token: string) => request<Checkin>('/checkins/hoje', { token }),

  listCheckins: (token: string, limite = 30) =>
    request<Checkin[]>(`/checkins?limite=${limite}`, { token }),

  getCheckin: (token: string, id: string) =>
    request<Checkin>(`/checkins/${encodeURIComponent(id)}`, { token }),
}
