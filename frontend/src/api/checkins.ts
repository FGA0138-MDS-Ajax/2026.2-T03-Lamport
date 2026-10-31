
import { request } from './client'

export type Tag =
  | 'humor'
  | 'ansiedade'
  | 'sono'
  | 'estresse'
  | 'bem_estar'
  | 'ajuda_profissional'

export interface Checkin {
  id: string
  data: string
  pensamento_risco: boolean
  humor: number | null
  ansiedade: number | null
  sono: number | null
  sobrecarga: number | null
  nivel: string
  tags: Tag[]
  criado_em: string
}

export interface CheckinPagination {
  items: Checkin[]
  total: number
  limit: number
  offset: number
}

export const checkinsApi = {
  list: (token: string, limit = 30, offset = 0) =>
    request<CheckinPagination>(
      `/checkins?limit=${limit}&offset=${offset}`,
      { token },
    ),
}
