import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { mockApi, renderApp, testUser } from '../test/utils'

const token = 'header.payload.signature'

// Usuário já autenticado na página inicial, com a sessão guardada no navegador.
async function openHomeAuthenticated(routes: Parameters<typeof mockApi>[0] = {}) {
  sessionStorage.setItem('sintoniza.token', token)
  const fetchMock = mockApi({ 'GET /api/me': { status: 200, body: testUser }, ...routes })
  renderApp('/')
  await screen.findByRole('heading', { name: 'Olá!' })
  return { fetchMock, user: userEvent.setup() }
}

function deleteCalls(fetchMock: ReturnType<typeof mockApi>) {
  return fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')
}

describe('ExcluirConta (R04)', () => {
  it('asks for confirmation warning that all data will be erased permanently', async () => {
    const { fetchMock, user } = await openHomeAuthenticated()

    await user.click(screen.getByRole('button', { name: 'Excluir conta' }))

    const dialog = screen.getByRole('alertdialog', { name: 'Excluir sua conta?' })
    expect(dialog).toHaveAccessibleDescription(
      /check-ins, avaliações e recomendações.*sem possibilidade de recuperação/,
    )
    expect(within(dialog).getByRole('button', { name: 'Cancelar' })).toHaveFocus()
    expect(deleteCalls(fetchMock)).toHaveLength(0)
  })

  it('does not delete the account when the user cancels', async () => {
    const { fetchMock, user } = await openHomeAuthenticated()

    await user.click(screen.getByRole('button', { name: 'Excluir conta' }))
    await user.click(screen.getByRole('button', { name: 'Cancelar' }))

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Excluir conta' })).toHaveFocus()
    expect(screen.getByRole('heading', { name: 'Olá!' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBe(token)
    expect(deleteCalls(fetchMock)).toHaveLength(0)
  })

  it('calls DELETE /api/me, clears the session and redirects on confirmation', async () => {
    const { fetchMock, user } = await openHomeAuthenticated({
      'DELETE /api/me': { status: 204 },
    })

    await user.click(screen.getByRole('button', { name: 'Excluir conta' }))
    await user.click(screen.getByRole('button', { name: 'Excluir definitivamente' }))

    // A página inicial é privada: sem sessão, o guard leva ao login.
    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBeNull()

    const calls = deleteCalls(fetchMock)
    expect(calls).toHaveLength(1)
    const [input, init] = calls[0]
    expect(new URL(String(input)).pathname).toBe('/api/me')
    expect(init?.headers).toMatchObject({ Authorization: `Bearer ${token}` })
  })

  it('keeps the session and shows an error when the deletion fails', async () => {
    const { user } = await openHomeAuthenticated({
      'DELETE /api/me': { status: 503 },
    })

    await user.click(screen.getByRole('button', { name: 'Excluir conta' }))
    await user.click(screen.getByRole('button', { name: 'Excluir definitivamente' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/indisponível no momento/)
    expect(screen.getByRole('heading', { name: 'Olá!' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBe(token)
    expect(screen.getByRole('button', { name: 'Excluir definitivamente' })).toBeEnabled()
  })
})
