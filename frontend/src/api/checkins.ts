import { request } from './client'

export interface CreateCheckinData {
  humor: number | null
  ansiedade: number | null
  sono: number | null
  sobrecarga: number | null
  pensamento_risco: boolean
}

export type Nivel =
  | 'autocuidado'
  | 'atencao'
  | 'prioritario'
  | 'crise'

export type Tag =
  | 'HUMOR'
  | 'ANSIEDADE'
  | 'SONO'
  | 'ESTRESSE'
  | 'BEM_ESTAR'
  | 'AJUDA_PROFISSIONAL'

export interface Checkin {
  id: string
  data: string
  humor: number | null
  ansiedade: number | null
  sono: number | null
  sobrecarga: number | null
  pensamento_risco: boolean
  nivel: Nivel
  tags: Tag[]
}

export const checkinsApi = {
  createCheckin: (token: string, data: CreateCheckinData) =>
    request<Checkin>('/checkins', {
      method: 'POST',
      body: data,
      token,
    }),

  getTodayCheckin: (token: string) =>
    request<Checkin>('/checkins/hoje', { token }),

  listCheckins: (token: string, limite = 30) =>
    request<Checkin[]>(`/checkins?limite=${limite}`, {
      token,
    }),

  getCheckin: (token: string, id: string) =>
    request<Checkin>(`/checkins/${encodeURIComponent(id)}`, { token }),
}
