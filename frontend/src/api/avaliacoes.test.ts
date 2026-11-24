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
  orientacao:
    'Continue acompanhando como você está. Seguem materiais de autocuidado.',
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

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('avaliacoesApi', () => {
  describe('createAvaliacao', () => {
    it('envia as respostas ao backend e retorna o resultado da avaliação', async () => {
      const fetchMock = vi.fn().mockResolvedValue(
        new Response(JSON.stringify(respostaAvaliacao), {
          status: 201,
          headers: { 'Content-Type': 'application/json' },
        }),
      )

      vi.stubGlobal('fetch', fetchMock)

      const resultado = await avaliacoesApi.createAvaliacao(
        token,
        dadosAvaliacao,
      )

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
      const fetchMock = vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Respostas inválidas' }), {
          status: 422,
          headers: { 'Content-Type': 'application/json' },
        }),
      )

      vi.stubGlobal('fetch', fetchMock)

      await expect(
        avaliacoesApi.createAvaliacao(token, dadosAvaliacao),
      ).rejects.toMatchObject({
        name: 'ApiError',
        status: 422,
        message: 'Respostas inválidas',
      })
    })
  })

  describe('listAvaliacoes', () => {
    it('lista as avaliações sem retornar os detalhes das recomendações', async () => {
      const resultado = await avaliacoesApi.listAvaliacoes(token)

      expect(resultado.length).toBeGreaterThan(0)

      expect(resultado[0]).toMatchObject({
        id: expect.any(String),
        criado_em: expect.any(String),
        escore_phq9: expect.any(Number),
        escore_gad7: expect.any(Number),
        faixa_phq9: expect.any(String),
        faixa_gad7: expect.any(String),
        nivel: expect.any(String),
      })

      expect(resultado[0]).not.toHaveProperty('recomendacoes')
      expect(resultado[0]).not.toHaveProperty('orientacao')
      expect(resultado[0]).not.toHaveProperty('respostas_phq9')
      expect(resultado[0]).not.toHaveProperty('respostas_gad7')
    })
  })

  describe('getAvaliacao', () => {
    it('consulta uma avaliação pelo ID', async () => {
      const resultado = await avaliacoesApi.getAvaliacao(token, '1')

      expect(resultado).toMatchObject({
        id: '1',
        escore_phq9: 3,
        escore_gad7: 4,
        faixa_phq9: 'minima',
        faixa_gad7: 'minima',
        nivel: 'autocuidado',
        respostas_phq9: [1, 0, 1, 0, 0, 1, 0, 0, 0],
        respostas_gad7: [1, 0, 1, 0, 1, 0, 1],
      })

      expect(resultado.recomendacoes).toBeDefined()
      expect(resultado.orientacao).toBeTruthy()
      expect(resultado.criado_em).toBeTruthy()
    })

    it('retorna erro ao consultar uma avaliação inexistente', async () => {
      await expect(
        avaliacoesApi.getAvaliacao(token, 'id-inexistente'),
      ).rejects.toThrow('Avaliação não encontrada')
    })
  })
})
