import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mockApi, renderApp, testUser } from '../test/utils'

const notFound = { status: 404, body: { detail: 'Check-in not found' } }

// TI-03: P1 = 4, P2 = 3, P3 = 1, P4 = 0, P5 = Não → tags ANSIEDADE e SONO, regras R-D3 e R-D4.
const recomendacoes = [
  {
    titulo: 'Ansiedade: como lidar',
    fonte: 'Ministério da Saúde',
    resumo: 'Orientações para reconhecer e lidar com a ansiedade no dia a dia.',
    url: 'https://www.gov.br/saude/ansiedade',
    regra: 'R-D3',
    motivo: 'Você indicou ter se sentido bastante ou extremamente ansioso(a) hoje.',
  },
  {
    titulo: 'Dicas para dormir melhor',
    fonte: 'Biblioteca Virtual em Saúde',
    resumo: 'Hábitos que ajudam a ter uma noite de sono melhor.',
    url: 'https://bvsms.saude.gov.br/dormir-bem',
    regra: 'R-D4',
    motivo: 'Você indicou que dormiu mal na última noite.',
  },
]

const criado = { nivel: 'autocuidado', tags: ['ansiedade', 'sono'], recomendacoes }
const hoje = { p1: 4, p2: 3, p3: 1, p4: 0, p5: false, ...criado }

async function answerTi03AndSubmit() {
  const user = userEvent.setup()
  await user.selectOptions(await screen.findByLabelText(/Como você está se sentindo/), '4')
  await user.selectOptions(screen.getByLabelText(/ansioso/), '3')
  await user.selectOptions(screen.getByLabelText(/qualidade do seu sono/), '1')
  await user.selectOptions(screen.getByLabelText(/sobrecarregado/), '0')
  await user.selectOptions(screen.getByLabelText(/pensamentos de se machucar/), 'false')
  await user.click(screen.getByRole('button', { name: 'Enviar check-in' }))
}

async function expectMaterials() {
  expect(
    await screen.findByRole('heading', { name: 'Conteúdos para hoje', level: 1 }),
  ).toBeInTheDocument()
  const cards = screen.getAllByRole('article')
  expect(cards).toHaveLength(2)
  recomendacoes.forEach((recomendacao, index) => {
    const card = within(cards[index])
    expect(card.getByRole('heading', { name: recomendacao.titulo })).toBeInTheDocument()
    expect(card.getByText(`Fonte: ${recomendacao.fonte}`)).toBeInTheDocument()
    expect(card.getByText(recomendacao.resumo)).toBeInTheDocument()
    expect(card.getByText('Por que estou vendo isto?')).toBeInTheDocument()
    expect(card.getByText(recomendacao.motivo)).toBeInTheDocument()

    const link = card.getByRole('link', {
      name: new RegExp(`Abrir no site oficial.*${recomendacao.titulo}`),
    })
    expect(link).toHaveAttribute('href', recomendacao.url)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })
}

describe('DailyCheckin sem risco (R06, R-S5)', () => {
  beforeEach(() => {
    sessionStorage.setItem('sintoniza.token', 'header.payload.signature')
  })

  it('mostra os materiais e os motivos após o envio', async () => {
    const fetchMock = mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': notFound,
      'POST /api/checkins': { status: 201, body: criado },
    })
    renderApp('/dailycheckin')

    await answerTi03AndSubmit()

    expect(await screen.findByText('Check-in de hoje registrado.')).toBeInTheDocument()
    await expectMaterials()
    expect(screen.getByRole('heading', { name: 'Conteúdos para hoje' })).toHaveFocus()
    expect(screen.getByRole('link', { name: 'Ver histórico' })).toHaveAttribute(
      'href',
      '/historico',
    )
    expect(screen.getByRole('link', { name: 'Voltar ao início' })).toHaveAttribute('href', '/')
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST')
    expect(JSON.parse(post![1]!.body as string)).toEqual({ p1: 4, p2: 3, p3: 1, p4: 0, p5: false })
  })

  it('mostra o resultado gravado do dia ao reabrir o check-in', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': { status: 200, body: hoje },
    })
    renderApp('/dailycheckin')

    await expectMaterials()
    expect(
      screen.getByText('Você já fez o check-in de hoje. Um novo check-in fica disponível amanhã.'),
    ).toBeInTheDocument()
    expect(screen.queryByText('Check-in de hoje registrado.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Enviar check-in' })).not.toBeInTheDocument()
  })

  it('mostra o resultado do dia quando o envio responde 409', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': [notFound, { status: 200, body: hoje }],
      'POST /api/checkins': { status: 409, body: { detail: 'Check-in already done today' } },
    })
    renderApp('/dailycheckin')

    await answerTi03AndSubmit()

    await expectMaterials()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('avisa quando não há materiais (R-S6)', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': { status: 200, body: { ...hoje, recomendacoes: [] } },
    })
    renderApp('/dailycheckin')

    expect(
      await screen.findByText(
        'Não encontramos materiais para hoje. Continue acompanhando como você está.',
      ),
    ).toBeInTheDocument()
    expect(screen.queryByRole('article')).not.toBeInTheDocument()
  })

  it('mantém o formulário e mostra o erro quando o envio falha', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': notFound,
      'POST /api/checkins': { status: 503, body: { detail: 'Unavailable' } },
    })
    renderApp('/dailycheckin')

    await answerTi03AndSubmit()

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível enviar o check-in. Tente novamente.',
    )
    expect(screen.getByRole('button', { name: 'Enviar check-in' })).toBeEnabled()
  })
})

// R-D1: nível CRISE, sem tags e sem recomendações.
const crise = { nivel: 'crise', tags: [], recomendacoes: [] }

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

  it('opens the help screen, without materials, when reopening a crisis check-in', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'GET /api/checkins/hoje': {
        status: 200,
        body: { p1: null, p2: null, p3: null, p4: null, p5: true, ...crise },
      },
    })
    renderApp('/dailycheckin')

    expect(
      await screen.findByRole('heading', { name: 'Ajuda Imediata', level: 1 }),
    ).toBeInTheDocument()
    expect(screen.queryByText('Conteúdos para hoje')).not.toBeInTheDocument()
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
