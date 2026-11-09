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
  listCheckinsMock.mockResolvedValue(items)
}

describe('HistoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSuccessfulResponse()
  })

  it('exibe os check-ins com suas respectivas datas', async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText('30 de out')).toBeInTheDocument()
    })

    expect(screen.getAllByText('29 de out')).toHaveLength(2)
    expect(screen.getByText('27 de out')).toBeInTheDocument()

    expect(screen.getAllByText(/Humor:/)).toHaveLength(4)
  })

  it('exibe "Não informado" quando humor é nulo', async () => {
    render(<HistoryPage />)

    expect(await screen.findByText('Não informado')).toBeInTheDocument()
  })

  it('exibe os check-ins em ordem cronológica decrescente', async () => {
    const { container } = render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText('30 de out')).toBeInTheDocument()
    })

    const dates = Array.from(container.querySelectorAll('.history-date')).map(
      (element) => element.textContent,
    )

    expect(dates).toEqual(['30 de out', '29 de out', '29 de out', '27 de out'])
  })

  it('exibe uma mensagem quando ocorre um erro', async () => {
    listCheckinsMock.mockRejectedValue(new Error('Erro ao carregar check-ins'))

    render(<HistoryPage />)

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })

  it('chama a API com o token e o limite', async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(listCheckinsMock).toHaveBeenCalledWith('test-token', 30)
    })
  })
})
