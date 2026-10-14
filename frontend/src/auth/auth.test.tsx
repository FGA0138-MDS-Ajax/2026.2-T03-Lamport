import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { mockApi, renderApp, testUser } from '../test/utils'

const token = 'header.payload.signature'

async function submitLogin(password: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('E-mail'), testUser.email)
  await user.type(screen.getByLabelText('Senha'), password)
  await user.click(screen.getByRole('button', { name: 'Entrar' }))
  return user
}

describe('authentication flow', () => {
  it('redirects anonymous users from private pages to login', async () => {
    mockApi({})
    renderApp('/')

    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('shows an error for invalid credentials', async () => {
    mockApi({
      'POST /api/auth/login': { status: 401, body: { detail: 'Invalid e-mail or password' } },
    })
    renderApp('/login')

    await submitLogin('senha-errada')

    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail ou senha incorretos.')
    expect(sessionStorage.getItem('sintoniza.token')).toBeNull()
  })

  it('tells the user to wait after too many failed attempts', async () => {
    mockApi({
      'POST /api/auth/login': {
        status: 429,
        body: { detail: 'Too many login attempts, try again later' },
      },
    })
    renderApp('/login')

    await submitLogin('senha-errada')

    expect(await screen.findByRole('alert')).toHaveTextContent(/Muitas tentativas sem sucesso/)
  })

  it('logs in, opens the private page and logs out', async () => {
    const fetchMock = mockApi({
      'POST /api/auth/login': {
        status: 200,
        body: { access_token: token, token_type: 'bearer', expires_in: 3600 },
      },
      'GET /api/users/me': { status: 200, body: testUser },
      'POST /api/auth/logout': { status: 204 },
    })
    renderApp('/login')

    const user = await submitLogin('senha-segura-123')

    expect(await screen.findByRole('heading', { name: 'Olá!' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBe(token)

    await user.click(screen.getByRole('button', { name: 'Sair' }))

    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBeNull()
    const [, logoutInit] = fetchMock.mock.calls.at(-1)!
    expect(logoutInit?.headers).toMatchObject({ Authorization: `Bearer ${token}` })
  })

  it('restores a stored session', async () => {
    sessionStorage.setItem('sintoniza.token', token)
    mockApi({ 'GET /api/users/me': { status: 200, body: testUser } })
    renderApp('/')

    expect(await screen.findByRole('heading', { name: 'Olá!' })).toBeInTheDocument()
  })

  it('discards a stored session rejected by the server', async () => {
    sessionStorage.setItem('sintoniza.token', token)
    mockApi({ 'GET /api/users/me': { status: 401, body: { detail: 'Not authenticated' } } })
    renderApp('/')

    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
    expect(sessionStorage.getItem('sintoniza.token')).toBeNull()
  })
})
