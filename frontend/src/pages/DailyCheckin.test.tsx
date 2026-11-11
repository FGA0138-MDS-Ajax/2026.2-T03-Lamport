import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mockApi, renderApp, testUser } from '../test/utils'

const crise = {
  id: 'c1',
  data: '2026-11-09',
  p1: null,
  p2: null,
  p3: null,
  p4: null,
  p5: true,
  nivel: 'crise',
  tags: [],
  criado_em: '2026-11-09T12:00:00Z',
}

async function answerP5WithYesAndSubmit() {
  const user = userEvent.setup()
  const p5 = await screen.findByLabelText(/pensamentos de se machucar/)
  await user.selectOptions(p5, 'true')
  await user.click(screen.getByRole('button', { name: 'Enviar check-in' }))
}

describe('DailyCheckin with P5 = Sim (R-D1)', () => {
  beforeEach(() => {
    sessionStorage.setItem('sintoniza.token', 'header.payload.signature')
    // GET /api/checkins/hoje responde 404 quando ainda não há check-in; a página registra no console.
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('opens the help screen after saving the check-in', async () => {
    const fetchMock = mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': { status: 404, body: { detail: 'Not found' } },
      'POST /api/checkins': { status: 201, body: crise },
    })
    renderApp('/dailycheckin')

    await answerP5WithYesAndSubmit()

    expect(
      await screen.findByRole('heading', { name: 'Ajuda Imediata', level: 1 }),
    ).toBeInTheDocument()
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST')
    expect(JSON.parse(post![1]!.body as string)).toMatchObject({ p5: true })
  })

  it('still opens the help screen when saving fails', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': { status: 404, body: { detail: 'Not found' } },
      'POST /api/checkins': { status: 503, body: { detail: 'Unavailable' } },
    })
    renderApp('/dailycheckin')

    await answerP5WithYesAndSubmit()

    expect(
      await screen.findByRole('heading', { name: 'Ajuda Imediata', level: 1 }),
    ).toBeInTheDocument()
  })
})
