import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TelaAjuda } from '../components/TelaAjuda'
import { mockApi, renderApp, testUser } from '../test/utils'

const AVISO =
  'O Sintoniza não acompanha suas respostas em tempo real e não avisa ninguém. Se você precisa de ajuda agora, use os contatos acima.'

function expectTelaAjuda() {
  expect(screen.getByRole('heading', { name: 'Ajuda Imediata', level: 1 })).toBeInTheDocument()
}

describe('TelaAjuda (Visão, seção 4.5.5)', () => {
  it('shows the CVV, SAMU, UPA, trusted person and monitoring notice', () => {
    render(<TelaAjuda />)

    const cvv = screen.getByRole('region', { name: 'CVV – Centro de Valorização da Vida' })
    expect(cvv).toHaveTextContent('Ligue 188, gratuito, 24 horas por dia.')
    expect(within(cvv).getByRole('link', { name: 'Ligue 188' })).toHaveAttribute('href', 'tel:188')
    const chat = within(cvv).getByRole('link', { name: 'Atendimento por chat no site cvv.org.br' })
    expect(chat).toHaveAttribute('href', 'https://cvv.org.br/chat/')
    expect(chat).toHaveAttribute('target', '_blank')
    expect(chat).toHaveAttribute('rel', 'noopener noreferrer')

    const samu = screen.getByRole('region', { name: 'SAMU' })
    expect(within(samu).getByRole('link', { name: 'Ligue 192' })).toHaveAttribute('href', 'tel:192')

    expect(
      screen.getByText('Em perigo imediato, procure a UPA ou o pronto-socorro mais próximo.'),
    ).toBeInTheDocument()
    expect(
      screen.getByText('Procure alguém de confiança e não fique sozinho(a).'),
    ).toBeInTheDocument()
    expect(screen.getByText(AVISO)).toBeInTheDocument()
  })

  it('uses unique ids for every labelled section', () => {
    const { container } = render(<TelaAjuda />)

    const ids = [...container.querySelectorAll('[id]')].map((el) => el.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const section of container.querySelectorAll('[aria-labelledby]')) {
      expect(container.querySelector(`#${section.getAttribute('aria-labelledby')}`)).not.toBeNull()
    }
  })
})

describe('Ajuda Imediata page', () => {
  it('opens without login and without calling the API', () => {
    const fetchMock = mockApi({})
    renderApp('/risco')

    expectTelaAjuda()
    expect(screen.getByText(AVISO)).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('works with the backend down', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))),
    )
    renderApp('/risco')

    expectTelaAjuda()
    expect(screen.getByRole('link', { name: 'Ligue 188' })).toHaveAttribute('href', 'tel:188')
  })

  it('opens for a logged-in user too', async () => {
    sessionStorage.setItem('sintoniza.token', 'header.payload.signature')
    mockApi({ 'GET /api/users/me': { status: 200, body: testUser } })
    renderApp('/risco')

    expect(await screen.findByRole('button', { name: 'Sair' })).toBeInTheDocument()
    expectTelaAjuda()
  })
})

describe('BotaoAjuda "Preciso de ajuda agora"', () => {
  it.each(['/login', '/cadastro'])(
    'is shown without login on %s and opens the help screen',
    async (path) => {
      const fetchMock = mockApi({})
      renderApp(path)

      await userEvent.click(screen.getByRole('link', { name: 'Preciso de ajuda agora' }))

      expectTelaAjuda()
      expect(fetchMock).not.toHaveBeenCalled()
    },
  )

  it('is shown on the privacy page', async () => {
    const fetchMock = mockApi({ 'GET /api/terms': { status: 200, body: { version: '2026-10' } } })
    renderApp('/privacidade')

    expect(
      screen.getByRole('heading', { name: 'Termos de uso e privacidade', level: 1 }),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Preciso de ajuda agora' })).toBeInTheDocument()
    await expect.poll(() => fetchMock.mock.calls.length).toBe(1)
  })

  it('is shown on the not found page', () => {
    mockApi({})
    renderApp('/pagina-que-nao-existe')

    expect(screen.getByRole('heading', { name: 'Página não encontrada' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Preciso de ajuda agora' })).toBeInTheDocument()
  })

  it('is shown once in the header for a logged-in user', async () => {
    sessionStorage.setItem('sintoniza.token', 'header.payload.signature')
    mockApi({
      'GET /api/users/me': { status: 200, body: testUser },
      'GET /api/checkins': { status: 200, body: [] },
    })
    renderApp('/historico')

    expect(await screen.findByRole('button', { name: 'Sair' })).toBeInTheDocument()
    const header = screen.getByRole('banner')
    expect(within(header).getAllByRole('link', { name: 'Preciso de ajuda agora' })).toHaveLength(1)
  })
})
