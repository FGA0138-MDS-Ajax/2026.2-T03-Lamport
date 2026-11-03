import { render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { HistoryPage } from './HistoryPage'
import type { Checkin } from '../api/checkins'

const { listCheckinsMock } = vi.hoisted(() => ({
  listCheckinsMock: vi.fn(),
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

function mockSuccessfulResponse(items = checkins) {
  listCheckinsMock.mockResolvedValue({
    items,
    total: items.length,
    limit: 30,
    offset: 0,
  })
}

describe('HistoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSuccessfulResponse()
  })

  it('exibe os check-ins agrupados por data', async () => {
    render(<HistoryPage />)

    expect(
      await screen.findByRole('heading', {
        name: '30 de outubro de 2026',
      }),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        name: '29 de outubro de 2026',
      }),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        name: '27 de outubro de 2026',
      }),
    ).toBeInTheDocument()

    expect(screen.getAllByText(/Humor:/)).toHaveLength(4)
  })

  it('exibe "Não informado" quando humor é nulo', async () => {
    render(<HistoryPage />)

    expect(await screen.findByText('Não informado')).toBeInTheDocument()
  })

  it('exibe os check-ins em ordem cronológica decrescente', async () => {
    render(<HistoryPage />)

    const newestDate = await screen.findByRole('heading', {
      name: '30 de outubro de 2026',
    })

    const oldestDate = screen.getByRole('heading', {
      name: '27 de outubro de 2026',
    })

    expect(
      newestDate.compareDocumentPosition(oldestDate) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
  })

  it('exibe uma mensagem quando ocorre um erro', async () => {
    listCheckinsMock.mockRejectedValue(new Error('Erro ao carregar check-ins'))

    render(<HistoryPage />)

    expect(
      await screen.findByRole('alert'),
    ).toBeInTheDocument()
  })

  it('chama a API com o token e os parâmetros de paginação', async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(listCheckinsMock).toHaveBeenCalledWith('test-token', 30, 0)
    })
  })
})