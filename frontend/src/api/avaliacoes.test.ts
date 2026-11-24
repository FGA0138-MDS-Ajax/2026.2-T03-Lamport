
import { describe, expect, it } from 'vitest'
import { avaliacoesApi } from './avaliacoes'

const token = 'test-token'

const dadosAvaliacao = {
  phq9: [1, 0, 2, 1, 0, 1, 0, 1, 0],
  gad7: [0, 1, 1, 0, 2, 0, 1],
}

describe('avaliacoesApi', () => {
  it('cria uma avaliação e retorna seus dados', async () => {
    const resultado = await avaliacoesApi.createAvaliacao(
      token,
      dadosAvaliacao,
    )

    expect(resultado).toMatchObject({
      respostas_phq9: dadosAvaliacao.phq9,
      respostas_gad7: dadosAvaliacao.gad7,
      escore_phq9: 6,
      escore_gad7: 5,
      faixa_phq9: 'MINIMA',
      faixa_gad7: 'MINIMA',
      nivel: 'autocuidado',
    })

    expect(resultado.id).toBeTruthy()
    expect(resultado.criado_em).toBeTruthy()
    expect(resultado.recomendacoes.length).toBeGreaterThan(0)
    expect(resultado.orientacao).toBeTruthy()
  })

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

  it('consulta uma avaliação pelo ID', async () => {
    const resultado = await avaliacoesApi.getAvaliacao(token, '1')

    expect(resultado).toMatchObject({
      id: '1',
      escore_phq9: 3,
      escore_gad7: 4,
      faixa_phq9: 'MINIMA',
      faixa_gad7: 'MINIMA',
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

  it('permite consultar uma avaliação recém-criada', async () => {
    const criada = await avaliacoesApi.createAvaliacao(
      token,
      dadosAvaliacao,
    )

    const consultada = await avaliacoesApi.getAvaliacao(
      token,
      criada.id,
    )

    expect(consultada).toEqual(criada)
  })

  it('mantém as avaliações criadas na listagem', async () => {
    const criada = await avaliacoesApi.createAvaliacao(
      token,
      dadosAvaliacao,
    )

    const lista = await avaliacoesApi.listAvaliacoes(token)

    expect(lista.some((item) => item.id === criada.id)).toBe(true)
  })
})
