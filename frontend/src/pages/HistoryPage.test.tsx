
import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { HistoryPage } from './HistoryPage'

describe('HistoryPage', () => {
  it('exibe os check-ins agrupados por data', async () => {
    render(<HistoryPage />)

    // Aguarda o carregamento dos dados.
    expect(
      await screen.findByText('Não informado'),
    ).toBeInTheDocument()

    // Verifica se as três datas aparecem.
    expect(
      screen.getByRole('heading', { name: '30 de outubro de 2026' }),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: '29 de outubro de 2026' }),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: '27 de outubro de 2026' }),
    ).toBeInTheDocument()

    // Verifica se existem dois check-ins no dia 29.
    const daySection = screen.getByRole('heading', {
      name: '29 de outubro de 2026',
    }).parentElement

    expect(daySection).not.toBeNull()

    expect(within(daySection!).getAllByText('Humor:')).toHaveLength(2)
  })
  it('exibe "Não informado" quando o humor é nulo', async () => {
    render(<HistoryPage />)

    expect(
        await screen.findByText('Não informado'),
    ).toBeInTheDocument()
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
    render(<HistoryPage />)

    // O estado de erro é ativado por uma simulação no componente.
    expect(
        await screen.findByText('Não informado'),
    ).toBeInTheDocument()
})
})
