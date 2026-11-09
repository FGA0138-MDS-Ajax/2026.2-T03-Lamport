import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { mockApi, renderApp } from '../test/utils'

describe('PrivacyPage', () => {
  it('shows the terms version provided by the API', async () => {
    mockApi({ 'GET /api/terms': { status: 200, body: { version: '2026-11' } } })
    renderApp('/privacidade')

    expect(await screen.findByText('Versão 2026-11')).toBeInTheDocument()
  })

  it('still shows the terms when the API is unavailable', async () => {
    const fetchMock = mockApi({ 'GET /api/terms': { status: 503 } })
    renderApp('/privacidade')

    expect(
      screen.getByRole('heading', { name: 'Termos de uso e privacidade', level: 1 }),
    ).toBeInTheDocument()
    await expect.poll(() => fetchMock.mock.calls.length).toBe(1)
    expect(screen.queryByText(/^Versão \d{4}-\d{2}$/)).not.toBeInTheDocument()
  })

  it('covers every item of the R03 acceptance criterion without login', async () => {
    const fetchMock = mockApi({ 'GET /api/terms': { status: 200, body: { version: '2026-11' } } })
    renderApp('/privacidade')

    // Página pública: não redireciona para o login.
    expect(screen.queryByRole('heading', { name: 'Entrar' })).not.toBeInTheDocument()

    // Dados coletados e finalidade de cada um.
    expect(
      screen.getByRole('heading', { name: 'Quais dados guardamos e para quê', level: 2 }),
    ).toBeInTheDocument()
    for (const name of [
      'Sua conta',
      'Seu aceite destes termos',
      'Respostas do check-in diário',
      'Respostas da avaliação quinzenal (PHQ-9 e GAD-7)',
      'Conteúdos sugeridos a você',
    ]) {
      expect(screen.getByRole('heading', { name, level: 3 })).toBeInTheDocument()
    }
    expect(screen.getAllByText('Para quê:').length).toBeGreaterThanOrEqual(3)

    // Sem diagnóstico e sem monitoramento.
    expect(screen.getByText('Não faz diagnóstico.')).toBeInTheDocument()
    expect(screen.getByText('Não monitora suas respostas.')).toBeInTheDocument()
    expect(screen.getByText(/não avisa ninguém/)).toBeInTheDocument()

    // Como excluir a conta (R04).
    expect(
      screen.getByRole('heading', { name: 'Como excluir sua conta', level: 2 }),
    ).toBeInTheDocument()
    expect(screen.getByText(/apagamos de forma definitiva/)).toBeInTheDocument()

    await expect.poll(() => fetchMock.mock.calls.length).toBe(1)
  })
})
