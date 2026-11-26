import { render, screen, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ResultadoAvaliacao } from '../api/avaliacoes'
import { AJUDA_PATH } from '../constants/ajuda'
import { mockApi } from '../test/utils'
import { ResultadoAvaliacaoPage } from './ResultadoAvaliacaoPage'

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    status: 'authenticated',
    user: null,
    token: 'test-token',
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

const AVALIACAO_ID = '550e8400-e29b-41d4-a716-446655440002'

// Perfil B do Quadro 19 (TSI-03): PHQ-9 = 10 (Moderada), GAD-7 = 5 (Leve), nível N2.
const perfilB: ResultadoAvaliacao = {
  escore_phq9: 10,
  escore_gad7: 5,
  faixa_phq9: 'moderada',
  faixa_gad7: 'leve',
  nivel: 'atencao',
  orientacao:
    'Recomendamos conversar com um profissional de saúde. No SUS, a porta de entrada é a Unidade Básica de Saúde (UBS).',
  recomendacoes: [
    {
      titulo: 'Saúde Mental – Saúde de A a Z',
      fonte: 'Ministério da Saúde',
      resumo: 'Explica o que é saúde mental.',
      url: 'https://www.gov.br/saude/saude-mental',
      regra: 'R-A3',
      motivo: 'Suas respostas indicam que conversar com um profissional de saúde pode ajudar.',
    },
    {
      titulo: 'Faça o que importa em tempos de estresse',
      fonte: 'OPAS/OMS',
      resumo: 'Guia ilustrado da OMS.',
      url: 'https://www.paho.org/pt/documentos/faca-que-importa',
      regra: 'R-A3',
      motivo: 'Seu resultado no PHQ-9 ficou na faixa moderada ou acima.',
    },
  ],
}

function renderAt(path: string, state?: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: path, state }]}>
      <Routes>
        <Route path="/avaliacoes/resultado" element={<ResultadoAvaliacaoPage />} />
        <Route path="/avaliacoes/:id" element={<ResultadoAvaliacaoPage />} />
        <Route path={AJUDA_PATH} element={<h1>Tela de Ajuda Imediata</h1>} />
      </Routes>
    </MemoryRouter>,
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('ResultadoAvaliacaoPage', () => {
  it('mostra o resultado do perfil B carregado por GET /api/avaliacoes/{id} (TSI-03)', async () => {
    const fetchMock = mockApi({
      [`GET /api/avaliacoes/${AVALIACAO_ID}`]: { status: 200, body: perfilB },
    })

    renderAt(`/avaliacoes/${AVALIACAO_ID}`)

    expect(
      await screen.findByRole('heading', { name: 'Resultado da avaliação' }),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(1)

    // Escores e faixas
    const phq9 = screen.getByRole('heading', { name: 'PHQ-9' }).closest('article')!
    expect(within(phq9).getByText('10')).toBeInTheDocument()
    expect(within(phq9).getByText(/de 27/)).toBeInTheDocument()
    expect(within(phq9).getByText('Faixa:').querySelector('strong')).toHaveTextContent('Moderada')

    const gad7 = screen.getByRole('heading', { name: 'GAD-7' }).closest('article')!
    expect(within(gad7).getByText('5')).toBeInTheDocument()
    expect(within(gad7).getByText(/de 21/)).toBeInTheDocument()
    expect(within(gad7).getByText('Faixa:').querySelector('strong')).toHaveTextContent('Leve')

    // Orientação de procurar a UBS
    expect(screen.getByRole('heading', { name: 'Procurar a UBS' })).toBeInTheDocument()
    expect(screen.getByText(/Unidade Básica de Saúde \(UBS\)/)).toBeInTheDocument()

    // Aviso de que não é diagnóstico (R09)
    expect(screen.getByText('Este resultado não é um diagnóstico.')).toBeInTheDocument()

    // 2 materiais com fonte, link em nova aba e motivo
    const materiais = screen.getAllByRole('article').filter((el) => el.querySelector('details'))
    expect(materiais).toHaveLength(2)
    const [primeiro] = materiais
    expect(within(primeiro).getByText('Fonte: Ministério da Saúde')).toBeInTheDocument()
    const link = within(primeiro).getByRole('link', { name: /Abrir no site oficial/ })
    expect(link).toHaveAttribute('href', 'https://www.gov.br/saude/saude-mental')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'))
    expect(within(primeiro).getByText('Por que estou vendo isto?')).toBeInTheDocument()

    expect(screen.queryByRole('link', { name: /Ajuda Imediata/ })).not.toBeInTheDocument()
  })

  it('mostra "não encontrada" quando a API responde 404 (avaliação de outro usuário)', async () => {
    mockApi({
      [`GET /api/avaliacoes/${AVALIACAO_ID}`]: {
        status: 404,
        body: { detail: 'Avaliacao not found' },
      },
    })

    renderAt(`/avaliacoes/${AVALIACAO_ID}`)

    expect(await screen.findByRole('alert')).toHaveTextContent('Avaliação não encontrada')
  })

  it('mostra "não encontrada" quando o id não é um UUID válido (422)', async () => {
    mockApi({
      'GET /api/avaliacoes/abc': { status: 422, body: { detail: [] } },
    })

    renderAt('/avaliacoes/abc')

    expect(await screen.findByRole('alert')).toHaveTextContent('Avaliação não encontrada')
  })

  it('mostra erro genérico quando a API falha', async () => {
    mockApi({
      [`GET /api/avaliacoes/${AVALIACAO_ID}`]: { status: 500, body: { detail: 'boom' } },
    })

    renderAt(`/avaliacoes/${AVALIACAO_ID}`)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível carregar a avaliação',
    )
  })

  it('mostra o resultado recém-registrado recebido pela navegação, sem chamar a API', () => {
    const fetchMock = mockApi({})

    renderAt('/avaliacoes/resultado', { resultado: perfilB })

    expect(screen.getByText('Avaliação registrada.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Procurar a UBS' })).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('no nível crise, esconde os materiais e leva à Tela de Ajuda Imediata', async () => {
    mockApi({
      [`GET /api/avaliacoes/${AVALIACAO_ID}`]: {
        status: 200,
        body: {
          ...perfilB,
          nivel: 'crise',
          orientacao: 'Procure a Tela de Ajuda Imediata para receber orientações.',
          recomendacoes: [],
        },
      },
    })

    renderAt(`/avaliacoes/${AVALIACAO_ID}`)

    const link = await screen.findByRole('link', { name: 'Ir para a Tela de Ajuda Imediata' })
    expect(link).toHaveAttribute('href', AJUDA_PATH)
    expect(
      screen.queryByRole('heading', { name: 'Materiais recomendados' }),
    ).not.toBeInTheDocument()
  })
})
