import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it } from 'vitest'
import { GAD7, PHQ9 } from '../constants/questionarioAvaliacao'
import { mockApi, renderApp, testUser } from '../test/utils'

// Perfil B do Quadro 19 (TSI-03): PHQ-9 = 10 (Moderada), GAD-7 = 5 (Leve), nível N2.
const PERFIL_B = { phq9: [2, 2, 1, 1, 1, 1, 1, 1, 0], gad7: [1, 1, 1, 1, 1, 0, 0] }

const resultadoPerfilB = {
  escore_phq9: 10,
  escore_gad7: 5,
  faixa_phq9: 'moderada',
  faixa_gad7: 'leve',
  nivel: 'atencao',
  orientacao: 'Recomendamos conversar com um profissional de saúde.',
  recomendacoes: [],
}

const LABELS = ['Nenhuma vez', 'Vários dias', 'Mais da metade dos dias', 'Quase todos os dias']

async function responder(respostas: { phq9: number[]; gad7: number[] }) {
  const user = userEvent.setup()
  for (const [instrumento, valores] of [
    [PHQ9, respostas.phq9],
    [GAD7, respostas.gad7],
  ] as const) {
    const parte = await screen.findByRole('region', { name: instrumento.title })
    for (const [index, valor] of valores.entries()) {
      const item = within(parte).getByRole('group', {
        name: `${index + 1}. ${instrumento.items[index]}`,
      })
      await user.click(within(item).getByRole('radio', { name: LABELS[valor] }))
    }
  }
  return user
}

function postCalls(fetchMock: ReturnType<typeof mockApi>) {
  return fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')
}

describe('AvaliacaoPage (R08, R10)', () => {
  beforeEach(() => {
    sessionStorage.setItem('sintoniza.token', 'header.payload.signature')
  })

  it('mostra os 16 itens, o aviso de periodicidade e o botão "Preciso de ajuda agora"', async () => {
    mockApi({ 'GET /api/me': { status: 200, body: testUser } })
    renderApp('/avaliacoes/nova')

    expect(
      await screen.findByRole('heading', { name: 'Avaliação quinzenal', level: 1 }),
    ).toBeInTheDocument()
    expect(screen.getByText(/o recomendado é responder a cada duas semanas/)).toBeInTheDocument()
    expect(screen.getByText(PHQ9.stem)).toBeInTheDocument()
    expect(screen.getByText(GAD7.stem)).toBeInTheDocument()
    expect(screen.getAllByRole('group')).toHaveLength(16)
    expect(screen.getAllByRole('radio')).toHaveLength(64)
    expect(screen.queryAllByRole('radio', { checked: true })).toHaveLength(0)
    expect(screen.getByRole('link', { name: 'Preciso de ajuda agora' })).toBeInTheDocument()
  })

  it('bloqueia o envio com item sem resposta e lista as pendências', async () => {
    const fetchMock = mockApi({ 'GET /api/me': { status: 200, body: testUser } })
    renderApp('/avaliacoes/nova')

    // Responde só os itens 1 a 3 do PHQ-9 e 1 a 6 do GAD-7.
    const user = await responder({ phq9: [0, 0, 0], gad7: [0, 0, 0, 0, 0, 0] })
    await user.click(screen.getByRole('button', { name: 'Concluir avaliação' }))

    const alerta = screen.getByRole('alert')
    expect(alerta).toHaveTextContent('Responda a todas as perguntas para concluir a avaliação.')
    const pendencias = within(alerta).getAllByRole('link')
    expect(pendencias.map((link) => link.textContent)).toEqual([
      'PHQ-9, pergunta 4',
      'PHQ-9, pergunta 5',
      'PHQ-9, pergunta 6',
      'PHQ-9, pergunta 7',
      'PHQ-9, pergunta 8',
      'PHQ-9, pergunta 9',
      'GAD-7, pergunta 7',
    ])
    expect(screen.getAllByText('Responda esta pergunta.')).toHaveLength(7)
    expect(postCalls(fetchMock)).toHaveLength(0)
  })

  it('envio válido leva à tela de resultado (TSI-03, perfil B)', async () => {
    const fetchMock = mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'POST /api/avaliacoes': { status: 201, body: resultadoPerfilB },
    })
    renderApp('/avaliacoes/nova')

    const user = await responder(PERFIL_B)
    await user.click(screen.getByRole('button', { name: 'Concluir avaliação' }))

    expect(
      await screen.findByRole('heading', { name: 'Resultado da avaliação', level: 1 }),
    ).toBeInTheDocument()
    const [[, init]] = postCalls(fetchMock)
    expect(JSON.parse(String(init?.body))).toEqual(PERFIL_B)
  })

  it('item 9 do PHQ-9 ≥ 1 abre a Tela de Ajuda Imediata', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'POST /api/avaliacoes': {
        status: 201,
        body: { ...resultadoPerfilB, nivel: 'crise', orientacao: '' },
      },
    })
    renderApp('/avaliacoes/nova')

    const user = await responder({ ...PERFIL_B, phq9: [...PERFIL_B.phq9.slice(0, 8), 1] })
    await user.click(screen.getByRole('button', { name: 'Concluir avaliação' }))

    expect(
      await screen.findByRole('heading', { name: 'Ajuda Imediata', level: 1 }),
    ).toBeInTheDocument()
    expect(screen.queryByText('Resultado da avaliação')).not.toBeInTheDocument()
  })

  it('item 9 do PHQ-9 ≥ 1 abre a Tela de Ajuda mesmo se o envio falhar (D3)', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'POST /api/avaliacoes': { status: 500, body: { detail: 'erro' } },
    })
    renderApp('/avaliacoes/nova')

    const user = await responder({ ...PERFIL_B, phq9: [...PERFIL_B.phq9.slice(0, 8), 3] })
    await user.click(screen.getByRole('button', { name: 'Concluir avaliação' }))

    expect(
      await screen.findByRole('heading', { name: 'Ajuda Imediata', level: 1 }),
    ).toBeInTheDocument()
  })

  it('falha no envio sem risco mantém as respostas e mostra o erro', async () => {
    mockApi({
      'GET /api/me': { status: 200, body: testUser },
      'POST /api/avaliacoes': { status: 503, body: { detail: 'indisponível' } },
    })
    renderApp('/avaliacoes/nova')

    const user = await responder(PERFIL_B)
    await user.click(screen.getByRole('button', { name: 'Concluir avaliação' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'O serviço está indisponível no momento. Tente novamente em instantes.',
    )
    expect(screen.getAllByRole('radio', { checked: true })).toHaveLength(16)
    expect(screen.getByRole('button', { name: 'Concluir avaliação' })).toBeEnabled()
  })
})
