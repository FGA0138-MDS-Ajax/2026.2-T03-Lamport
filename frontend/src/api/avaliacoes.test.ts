import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  avaliacoesApi,
  type AvaliacaoListItem,
  type CreateAvaliacaoData,
  type ResultadoAvaliacao,
} from './avaliacoes'
import { mockApi } from '../test/utils'

const token = 'test-token'
const id = '550e8400-e29b-41d4-a716-446655440000'

const dados: CreateAvaliacaoData = {
  phq9: [1, 0, 2, 1, 0, 1, 0, 1, 0],
  gad7: [0, 1, 1, 0, 2, 0, 1],
}

const resultado: ResultadoAvaliacao = {
  escore_phq9: 6,
  escore_gad7: 5,
  faixa_phq9: 'leve',
  faixa_gad7: 'leve',
  nivel: 'autocuidado',
  orientacao: 'Continue acompanhando como você está. Seguem materiais de autocuidado.',
  recomendacoes: [
    {
      titulo: 'Cuidados com a saúde mental',
      fonte: 'Ministério da Saúde',
      resumo: 'Informações sobre práticas de autocuidado.',
      url: 'https://www.gov.br/saude',
      regra: 'R-A4',
      motivo: 'Material informativo para promoção do autocuidado.',
    },
  ],
}

const item: AvaliacaoListItem = {
  id,
  data: '2026-11-20',
  escore_phq9: 6,
  escore_gad7: 5,
  faixa_phq9: 'leve',
  faixa_gad7: 'leve',
  nivel: 'autocuidado',
}

describe('avaliacoesApi', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it('cria uma avaliação enviando as respostas do PHQ-9 e do GAD-7', async () => {
    const fetchMock = mockApi({
      'POST /api/avaliacoes': { status: 201, body: resultado },
    })

    const result = await avaliacoesApi.createAvaliacao(token, dados)

    expect(result).toEqual(resultado)
    expect(fetchMock).toHaveBeenCalledTimes(1)

    const [url, init] = fetchMock.mock.calls[0]

    expect(String(url)).toContain('/api/avaliacoes')
    expect(init?.method).toBe('POST')
    expect(init?.headers).toMatchObject({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    })
    expect(JSON.parse(String(init?.body))).toEqual(dados)
  })

  it('propaga erro 422 quando as respostas são inválidas', async () => {
    mockApi({
      'POST /api/avaliacoes': { status: 422, body: { detail: 'Respostas inválidas' } },
    })

    await expect(avaliacoesApi.createAvaliacao(token, dados)).rejects.toMatchObject({
      name: 'ApiError',
      status: 422,
      message: 'Respostas inválidas',
    })
  })

  it('lista o histórico de avaliações do usuário', async () => {
    const fetchMock = mockApi({
      'GET /api/avaliacoes': { status: 200, body: [item] },
    })

    const result = await avaliacoesApi.listAvaliacoes(token)

    expect(result).toEqual([item])

    const [, init] = fetchMock.mock.calls[0]

    expect(init?.method).toBe('GET')
    expect(init?.headers).toMatchObject({ Authorization: `Bearer ${token}` })
  })

  it('retorna lista vazia quando o usuário não possui avaliações', async () => {
    mockApi({
      'GET /api/avaliacoes': { status: 200, body: [] },
    })

    await expect(avaliacoesApi.listAvaliacoes(token)).resolves.toEqual([])
  })

  it('propaga erro 401 ao listar sem autenticação', async () => {
    mockApi({
      'GET /api/avaliacoes': { status: 401, body: { detail: 'Not authenticated' } },
    })

    await expect(avaliacoesApi.listAvaliacoes(token)).rejects.toMatchObject({
      name: 'ApiError',
      status: 401,
    })
  })

  it('busca uma avaliação pelo ID com os mesmos campos do POST', async () => {
    const fetchMock = mockApi({
      [`GET /api/avaliacoes/${id}`]: { status: 200, body: resultado },
    })

    const result = await avaliacoesApi.getAvaliacao(token, id)

    expect(result).toEqual(resultado)

    const [, init] = fetchMock.mock.calls[0]

    expect(init?.method).toBe('GET')
    expect(init?.headers).toMatchObject({ Authorization: `Bearer ${token}` })
  })

  it('propaga erro 404 para avaliação inexistente ou de outro usuário', async () => {
    mockApi({
      [`GET /api/avaliacoes/${id}`]: { status: 404, body: { detail: 'Avaliacao not found' } },
    })

    await expect(avaliacoesApi.getAvaliacao(token, id)).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
      message: 'Avaliacao not found',
    })
  })

  it('transforma erro de rede em ApiError com status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(avaliacoesApi.listAvaliacoes(token)).rejects.toMatchObject({
      name: 'ApiError',
      status: 0,
      message: 'Network error',
    })
  })
})
