import { render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { HistoryPage } from './HistoryPage'
import type { AvaliacaoListItem } from '../api/avaliacoes'
import type { Checkin } from '../api/checkins'

const { listCheckinsMock, listAvaliacoesMock } = vi.hoisted(() => ({
  listCheckinsMock: vi.fn(),
  listAvaliacoesMock: vi.fn(),
}))

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    status: 'authenticated',
    user: null,
    token: 'test-token',
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

vi.mock('../api/checkins', () => ({
  checkinsApi: {
    listCheckins: listCheckinsMock,
  },
}))

vi.mock('../api/avaliacoes', () => ({
  avaliacoesApi: {
    listAvaliacoes: listAvaliacoesMock,
  },
}))

function renderPage() {
  return render(
    <MemoryRouter>
      <HistoryPage />
    </MemoryRouter>,
  )
}

function avaliacoesSection() {
  return screen.getByRole('region', { name: 'Avaliações' })
}

function checkinsSection() {
  return screen.getByRole('region', { name: 'Check-ins' })
}

const checkins: Checkin[] = [
  {
    id: '1',
    data: '2026-10-30',
    p1: 4,
    p2: 2,
    p3: 3,
    p4: 1,
    p5: false,
    nivel: 'autocuidado',
    tags: ['HUMOR'],
    criado_em: '2026-10-30T12:00:00Z',
  },
  {
    id: '2',
    data: '2026-10-29',
    p1: 2,
    p2: 3,
    p3: 2,
    p4: 1,
    p5: false,
    nivel: 'atencao',
    tags: ['ANSIEDADE'],
    criado_em: '2026-10-29T12:00:00Z',
  },
  {
    id: '3',
    data: '2026-10-29',
    p1: null,
    p2: 3,
    p3: 2,
    p4: 1,
    p5: false,
    nivel: 'atencao',
    tags: ['SONO'],
    criado_em: '2026-10-29T13:00:00Z',
  },
  {
    id: '4',
    data: '2026-10-27',
    p1: 1,
    p2: 2,
    p3: 3,
    p4: 4,
    p5: false,
    nivel: 'prioritario',
    tags: ['ESTRESSE'],
    criado_em: '2026-10-27T12:00:00Z',
  },
]

const avaliacoes: AvaliacaoListItem[] = [
  {
    id: 'aval-1',
    data: '2026-11-15',
    escore_phq9: 3,
    escore_gad7: 10,
    faixa_phq9: 'minima',
    faixa_gad7: 'moderada',
    nivel: 'atencao',
  },
  {
    id: 'aval-2',
    data: '2026-11-01',
    escore_phq9: 16,
    escore_gad7: 15,
    faixa_phq9: 'moderadamente_grave',
    faixa_gad7: 'grave',
    nivel: 'prioritario',
  },
]

function mockSuccessfulResponse(items = checkins) {
  listCheckinsMock.mockResolvedValue(items)
  listAvaliacoesMock.mockResolvedValue(avaliacoes)
}

describe('HistoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSuccessfulResponse()
  })

  it('exibe os check-ins com suas respectivas datas', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('30 de out')).toBeInTheDocument()
    })

    expect(screen.getAllByText('29 de out')).toHaveLength(2)
    expect(screen.getByText('27 de out')).toBeInTheDocument()

    expect(screen.getAllByText(/Humor:/)).toHaveLength(4)
  })

  it('exibe "Não informado" quando humor é nulo', async () => {
    renderPage()

    expect(await screen.findByText('Não informado')).toBeInTheDocument()
  })

  it('exibe os check-ins em ordem cronológica decrescente', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('30 de out')).toBeInTheDocument()
    })

    const dates = Array.from(checkinsSection().querySelectorAll('.history-date')).map(
      (element) => element.textContent,
    )

    expect(dates).toEqual(['30 de out', '29 de out', '29 de out', '27 de out'])
  })

  it('exibe uma mensagem quando ocorre um erro', async () => {
    listCheckinsMock.mockRejectedValue(new Error('Erro ao carregar check-ins'))

    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível carregar o histórico. Tente novamente.',
    )
    expect(within(checkinsSection()).getByRole('alert')).toBeInTheDocument()
  })

  it('chama a API com o token e o limite', async () => {
    renderPage()

    await waitFor(() => {
      expect(listCheckinsMock).toHaveBeenCalledWith('test-token', 30)
    })
  })

  describe('avaliações', () => {
    it('exibe data, escores, faixas e nível de cada avaliação', async () => {
      renderPage()

      const links = await within(avaliacoesSection()).findAllByRole('link')
      expect(links).toHaveLength(2)

      expect(links[0]).toHaveTextContent('15 de nov')
      expect(links[0]).toHaveTextContent('PHQ-9: 3 · Mínima')
      expect(links[0]).toHaveTextContent('GAD-7: 10 · Moderada')
      expect(links[0]).toHaveTextContent('Nível: Procurar a UBS')

      expect(links[1]).toHaveTextContent('01 de nov')
      expect(links[1]).toHaveTextContent('PHQ-9: 16 · Moderadamente grave')
      expect(links[1]).toHaveTextContent('GAD-7: 15 · Grave')
      expect(links[1]).toHaveTextContent('Nível: Atenção prioritária')
    })

    it('cada avaliação leva à tela de resultado', async () => {
      renderPage()

      const links = await within(avaliacoesSection()).findAllByRole('link')

      expect(links[0]).toHaveAttribute('href', '/avaliacoes/aval-1')
      expect(links[1]).toHaveAttribute('href', '/avaliacoes/aval-2')
    })

    it('chama a API com o token', async () => {
      renderPage()

      await waitFor(() => {
        expect(listAvaliacoesMock).toHaveBeenCalledWith('test-token')
      })
    })

    it('exibe estado vazio quando não há avaliações', async () => {
      listAvaliacoesMock.mockResolvedValue([])

      renderPage()

      expect(
        await within(avaliacoesSection()).findByText('Você ainda não fez nenhuma avaliação.'),
      ).toBeInTheDocument()
      expect(within(avaliacoesSection()).queryByRole('link')).not.toBeInTheDocument()
    })

    it('exibe mensagem de erro quando a API de avaliações falha', async () => {
      listAvaliacoesMock.mockRejectedValue(new Error('Erro ao carregar avaliações'))

      renderPage()

      expect(await within(avaliacoesSection()).findByRole('alert')).toHaveTextContent(
        'Não foi possível carregar as avaliações. Tente novamente.',
      )
    })

    it('mantém os check-ins exibidos quando a API de avaliações falha', async () => {
      listAvaliacoesMock.mockRejectedValue(new Error('Erro ao carregar avaliações'))

      renderPage()

      await within(avaliacoesSection()).findByRole('alert')

      expect(within(checkinsSection()).getByText('30 de out')).toBeInTheDocument()
      expect(within(checkinsSection()).getAllByText(/Humor:/)).toHaveLength(4)
      expect(within(checkinsSection()).queryByRole('alert')).not.toBeInTheDocument()
    })

    it('mantém as avaliações exibidas quando a API de check-ins falha', async () => {
      listCheckinsMock.mockRejectedValue(new Error('Erro ao carregar check-ins'))

      renderPage()

      expect(await within(avaliacoesSection()).findAllByRole('link')).toHaveLength(2)
      expect(within(avaliacoesSection()).queryByRole('alert')).not.toBeInTheDocument()
    })
  })
})
