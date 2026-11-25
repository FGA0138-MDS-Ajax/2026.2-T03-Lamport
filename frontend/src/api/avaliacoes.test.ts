import { afterEach, describe, expect, it, vi } from 'vitest'
import { avaliacoesApi } from './avaliacoes'

const token = 'test-token'

const dadosAvaliacao = {
  phq9: [1, 0, 2, 1, 0, 1, 0, 1, 0],
  gad7: [0, 1, 1, 0, 2, 0, 1],
}

const respostaAvaliacao = {
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

const itemHistorico = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  data: '2026-11-20',
  escore_phq9: 6,
  escore_gad7: 5,
  faixa_phq9: 'leve',
  faixa_gad7: 'leve',
  nivel: 'autocuidado',
}

function criarResposta(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('avaliacoesApi', () => {
  describe('createAvaliacao', () => {
    it('envia as respostas ao backend e retorna o resultado da avaliação', async () => {
      const fetchMock = vi.fn().mockResolvedValue(criarResposta(respostaAvaliacao, 201))

      vi.stubGlobal('fetch', fetchMock)

      const resultado = await avaliacoesApi.createAvaliacao(token, dadosAvaliacao)

      expect(fetchMock).toHaveBeenCalledOnce()

      const [url, options] = fetchMock.mock.calls[0]

      expect(url).toBe('http://localhost:8000/api/avaliacoes')
      expect(options).toMatchObject({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(dadosAvaliacao),
      })

      expect(resultado).toEqual(respostaAvaliacao)
    })

    it('propaga erros retornados pelo backend', async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(criarResposta({ detail: 'Respostas inválidas' }, 422))

      vi.stubGlobal('fetch', fetchMock)

      await expect(avaliacoesApi.createAvaliacao(token, dadosAvaliacao)).rejects.toMatchObject({
        name: 'ApiError',
        status: 422,
        message: 'Respostas inválidas',
      })
    })
  })

  describe('listAvaliacoes', () => {
    it('consulta o histórico de avaliações do usuário', async () => {
      const fetchMock = vi.fn().mockResolvedValue(criarResposta([itemHistorico]))

      vi.stubGlobal('fetch', fetchMock)

      const resultado = await avaliacoesApi.listAvaliacoes(token)

      expect(fetchMock).toHaveBeenCalledOnce()

      const [url, options] = fetchMock.mock.calls[0]

      expect(url).toBe('http://localhost:8000/api/avaliacoes')
      expect(options).toMatchObject({
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      expect(resultado).toEqual([itemHistorico])
    })

    it('retorna uma lista vazia quando o usuário não possui avaliações', async () => {
      const fetchMock = vi.fn().mockResolvedValue(criarResposta([]))

      vi.stubGlobal('fetch', fetchMock)

      const resultado = await avaliacoesApi.listAvaliacoes(token)

      expect(resultado).toEqual([])
    })

    it('propaga erros retornados pelo backend', async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(criarResposta({ detail: 'Not authenticated' }, 401))

      vi.stubGlobal('fetch', fetchMock)

      await expect(avaliacoesApi.listAvaliacoes(token)).rejects.toMatchObject({
        name: 'ApiError',
        status: 401,
      })
    })
  })

  describe('getAvaliacao', () => {
    it('consulta uma avaliação pelo ID', async () => {
      const fetchMock = vi.fn().mockResolvedValue(criarResposta(respostaAvaliacao))

      vi.stubGlobal('fetch', fetchMock)

      const id = '550e8400-e29b-41d4-a716-446655440000'
      const resultado = await avaliacoesApi.getAvaliacao(token, id)

      expect(fetchMock).toHaveBeenCalledOnce()

      const [url, options] = fetchMock.mock.calls[0]

      expect(url).toBe(`http://localhost:8000/api/avaliacoes/${id}`)
      expect(options).toMatchObject({
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      expect(resultado).toEqual(respostaAvaliacao)
      expect(resultado).not.toHaveProperty('id')
      expect(resultado).not.toHaveProperty('criado_em')
      expect(resultado).not.toHaveProperty('respostas_phq9')
      expect(resultado).not.toHaveProperty('respostas_gad7')
    })

    it('propaga erro 404 ao consultar uma avaliação inexistente ou de outro usuário', async () => {
      const fetchMock = vi
        .fn()
        .mockResolvedValue(criarResposta({ detail: 'Avaliacao not found' }, 404))

      vi.stubGlobal('fetch', fetchMock)

      await expect(
        avaliacoesApi.getAvaliacao(token, '550e8400-e29b-41d4-a716-446655440000'),
      ).rejects.toMatchObject({
        name: 'ApiError',
        status: 404,
        message: 'Avaliacao not found',
      })
    })

    it('propaga erro 422 quando o ID possui formato inválido', async () => {
      const fetchMock = vi.fn().mockResolvedValue(criarResposta({ detail: [] }, 422))

      vi.stubGlobal('fetch', fetchMock)

      await expect(avaliacoesApi.getAvaliacao(token, 'id-invalido')).rejects.toMatchObject({
        name: 'ApiError',
        status: 422,
      })
    })
  })
})
