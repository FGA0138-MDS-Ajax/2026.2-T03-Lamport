import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { mockApi, renderApp } from '../test/utils'

describe('PrivacyPage', () => {
  it('shows the terms version provided by the API', async () => {
    mockApi({ 'GET /api/terms': { status: 200, body: { version: '2026-10' } } })
    renderApp('/privacidade')

    expect(await screen.findByText('Versão 2026-10')).toBeInTheDocument()
  })

  it('still shows the terms when the API is unavailable', async () => {
    const fetchMock = mockApi({ 'GET /api/terms': { status: 503 } })
    renderApp('/privacidade')

    expect(
      screen.getByRole('heading', { name: 'Termos de uso e privacidade', level: 1 }),
    ).toBeInTheDocument()
    await expect.poll(() => fetchMock.mock.calls.length).toBe(1)
    expect(screen.queryByText(/^Versão/)).not.toBeInTheDocument()
  })
})
