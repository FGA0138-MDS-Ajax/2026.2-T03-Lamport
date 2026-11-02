import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from './client'
import { checkinsApi, type Checkin } from './checkins'
import { mockApi } from '../test/utils'

const token = 'test-token'

const checkin: Checkin = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  data: '2026-10-30',
  humor: 3,
  ansiedade: 2,
  sono: 4,
  sobrecarga: 1,
  pensamento_risco: false,
  nivel: 'atencao',
  tags: ['ANSIEDADE'],
}

describe('checkinsApi', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it('propaga erro 409 quando o check-in do dia já foi realizado', async () => {
    mockApi({
      'POST /api/checkins': {
        status: 409,
        body: { detail: 'Check-in já realizado hoje' },
      },
    })

    await expect(
      checkinsApi.createCheckin(token, {
        humor: 3,
        ansiedade: 2,
        sono: 4,
        sobrecarga: 1,
        pensamento_risco: false,
      }),
    ).rejects.toMatchObject({
      name: 'ApiError',
      status: 409,
    })
  })

  it('propaga erro 422 quando os dados são inválidos', async () => {
    mockApi({
      'POST /api/checkins': {
        status: 422,
        body: { detail: 'Dados inválidos' },
      },
    })

    await expect(
      checkinsApi.createCheckin(token, {
        humor: 3,
        ansiedade: 2,
        sono: 4,
        sobrecarga: 1,
        pensamento_risco: false,
      }),
    ).rejects.toMatchObject({
      name: 'ApiError',
      status: 422,
    })
  })

  it('transforma erro de rede em ApiError com status 0', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    vi.stubGlobal('fetch', fetchMock)

    await expect(checkinsApi.getTodayCheckin(token)).rejects.toMatchObject({
      name: 'ApiError',
      status: 0,
      message: 'Network error',
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('cria um check-in enviando os campos esperados pelo backend', async () => {
    const fetchMock = mockApi({
      'POST /api/checkins': {
        status: 201,
        body: checkin,
      },
    })

    const data = {
      humor: 3,
      ansiedade: 2,
      sono: 4,
      sobrecarga: 1,
      pensamento_risco: false,
    }

    const result = await checkinsApi.createCheckin(token, data)

    expect(result).toEqual(checkin)
    expect(fetchMock).toHaveBeenCalledTimes(1)

    const [url, init] = fetchMock.mock.calls[0]

    expect(String(url)).toContain('/api/checkins')
    expect(init?.method).toBe('POST')
    expect(init?.headers).toMatchObject({
      Authorization: `Bearer ${token}`,
    })
    expect(JSON.parse(String(init?.body))).toEqual(data)
  })

  it('busca o check-in de hoje', async () => {
    const fetchMock = mockApi({
      'GET /api/checkins/hoje': {
        status: 200,
        body: checkin,
      },
    })

    const result = await checkinsApi.getTodayCheckin(token)

    expect(result).toEqual(checkin)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('lista check-ins com limite', async () => {
    const fetchMock = mockApi({
      'GET /api/checkins': {
        status: 200,
        body: [checkin],
      },
    })

    const result = await checkinsApi.listCheckins(token)

    expect(result).toEqual([checkin])

    const [url] = fetchMock.mock.calls[0]
    const parsedUrl = new URL(String(url))

    expect(parsedUrl.pathname).toBe('/api/checkins')
    expect(parsedUrl.searchParams.get('limite')).toBe('30')
  })

  it('busca um check-in pelo ID', async () => {
    const fetchMock = mockApi({
      'GET /api/checkins/550e8400-e29b-41d4-a716-446655440000': {
        status: 200,
        body: checkin,
      },
    })

    const result = await checkinsApi.getCheckin(token, checkin.id)

    expect(result).toEqual(checkin)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('propaga erro 404 ao buscar um check-in inexistente', async () => {
    mockApi({
      'GET /api/checkins/550e8400-e29b-41d4-a716-446655440000': {
        status: 404,
        body: { detail: 'Check-in não encontrado' },
      },
    })

    await expect(checkinsApi.getCheckin(token, checkin.id)).rejects.toBeInstanceOf(ApiError)
  })

  it('lança ApiError quando o token é inválido', async () => {
    mockApi({
      'GET /api/checkins/hoje': {
        status: 401,
        body: { detail: 'Token inválido' },
      },
    })

    await expect(checkinsApi.getTodayCheckin(token)).rejects.toBeInstanceOf(ApiError)
  })
})
