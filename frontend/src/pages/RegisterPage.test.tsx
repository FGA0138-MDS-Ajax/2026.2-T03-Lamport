import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { mockApi, renderApp, testUser } from '../test/utils'

async function fillForm(password = 'senha-segura-123', confirmation = password) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
  await user.type(screen.getByLabelText('Senha'), password)
  await user.type(screen.getByLabelText('Confirme a senha'), confirmation)
  await user.click(screen.getByRole('checkbox'))
  return user
}

describe('RegisterPage', () => {
  it('validates fields before calling the API', async () => {
    const fetchMock = mockApi({})
    renderApp('/cadastro')

    await userEvent.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(screen.getByText('Informe seu e-mail.')).toBeInTheDocument()
    expect(screen.getByText('Crie uma senha.')).toBeInTheDocument()
    expect(screen.getByText(/aceitar os termos de uso/)).toBeInTheDocument()
    expect(screen.getByLabelText('E-mail')).toHaveAttribute('aria-invalid', 'true')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('requires matching passwords', async () => {
    const fetchMock = mockApi({})
    renderApp('/cadastro')

    const user = await fillForm('senha-segura-123', 'outra-senha-123')
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(screen.getByText('As senhas informadas não coincidem.')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('creates the account and redirects to login', async () => {
    const fetchMock = mockApi({ 'POST /api/auth/register': { status: 201, body: testUser } })
    renderApp('/cadastro')

    const user = await fillForm()
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(await screen.findByText(/Conta criada com sucesso/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
    expect(screen.getByLabelText('E-mail')).toHaveValue('ana@example.com')
    expect(JSON.parse(fetchMock.mock.calls[0][1]!.body as string)).toEqual({
      email: 'ana@example.com',
      password: 'senha-segura-123',
      accept_terms: true,
    })
  })

  it('reports an e-mail that is already registered', async () => {
    mockApi({
      'POST /api/auth/register': { status: 409, body: { detail: 'E-mail already registered' } },
    })
    renderApp('/cadastro')

    const user = await fillForm()
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(await screen.findByText(/Este e-mail já está cadastrado/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Criar conta' })).toBeEnabled()
  })

  it('reports server errors', async () => {
    mockApi({ 'POST /api/auth/register': { status: 503, body: { detail: 'Unavailable' } } })
    renderApp('/cadastro')

    const user = await fillForm()
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/indisponível/)
  })
})
