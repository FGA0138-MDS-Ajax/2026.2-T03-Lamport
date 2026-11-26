import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/AuthContext'
import { avaliacoesApi } from '../api/avaliacoes'
import { describeError } from '../api/client'
import { AJUDA_PATH } from '../constants/ajuda'
import {
  INSTRUMENTOS,
  OPCOES_FREQUENCIA,
  PHQ9_ITEM_RISCO,
  type Instrumento,
} from '../constants/questionarioAvaliacao'

type Respostas = Record<Instrumento['id'], (number | undefined)[]>

const itemId = (instrumento: Instrumento, index: number) => `${instrumento.id}-item-${index + 1}`

// Textos do Quadro 12 do vocabulário da avaliação (#52).
const ERROS_POR_STATUS: Record<number, string> = {
  0: 'Não foi possível enviar sua avaliação. Suas respostas foram mantidas: verifique sua conexão e tente novamente.',
  401: 'Sua sessão expirou. Entre novamente para responder à avaliação.',
  422: 'Não foi possível registrar suas respostas. Revise-as e tente novamente.',
}

/** Avaliação quinzenal com o PHQ-9 e o GAD-7 (Visão, seção 4.5.2; R08 e R10). */
export function AvaliacaoPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [respostas, setRespostas] = useState<Respostas>({ phq9: [], gad7: [] })
  const [tentouConcluir, setTentouConcluir] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pendentes = INSTRUMENTOS.flatMap((instrumento) =>
    instrumento.items
      .map((_, index) => ({ instrumento, index }))
      .filter(({ index }) => respostas[instrumento.id][index] === undefined),
  )

  function responder(instrumento: Instrumento, index: number, valor: number) {
    setRespostas((prev) => {
      const lista = [...prev[instrumento.id]]
      lista[index] = valor
      return { ...prev, [instrumento.id]: lista }
    })
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (submitting) return
    setTentouConcluir(true)
    // As 16 respostas são obrigatórias (decisão D2): sem elas, nada é enviado.
    if (pendentes.length > 0) return

    const dados = { phq9: respostas.phq9 as number[], gad7: respostas.gad7 as number[] }
    const hasRisk = dados.phq9[PHQ9_ITEM_RISCO] >= 1

    setSubmitting(true)
    setError(null)
    try {
      const resultado = await avaliacoesApi.createAvaliacao(token as string, dados)
      if (hasRisk || resultado.nivel === 'crise') navigate(AJUDA_PATH)
      else navigate('/avaliacoes/resultado', { state: { resultado } })
    } catch (err) {
      // Por segurança, o item 9 diferente de "Nenhuma vez" leva à Tela de Ajuda mesmo se o
      // envio falhar (decisão D3).
      if (hasRisk) {
        navigate(AJUDA_PATH)
        return
      }
      setError(describeError(err, ERROS_POR_STATUS))
      setSubmitting(false)
    }
  }

  return (
    <section className="card" aria-labelledby="avaliacao-title">
      <h1 id="avaliacao-title">Avaliação quinzenal</h1>
      <p>São 16 perguntas sobre as últimas duas semanas. Todas são obrigatórias.</p>
      <p className="muted">
        Você pode responder quando quiser, mas o recomendado é responder a cada duas semanas, o
        período a que as perguntas se referem.
      </p>

      <form onSubmit={handleSubmit} noValidate>
        {INSTRUMENTOS.map((instrumento, parte) => (
          <section
            key={instrumento.id}
            className="avaliacao-parte"
            aria-labelledby={`${instrumento.id}-title`}
          >
            <p className="muted">
              Parte {parte + 1} de {INSTRUMENTOS.length} · {instrumento.items.length} perguntas
            </p>
            <h2 id={`${instrumento.id}-title`}>{instrumento.title}</h2>
            <p>{instrumento.stem}</p>

            {instrumento.items.map((texto, index) => {
              const id = itemId(instrumento, index)
              const valor = respostas[instrumento.id][index]
              const invalido = tentouConcluir && valor === undefined
              return (
                <fieldset
                  key={id}
                  id={id}
                  className="avaliacao-item"
                  aria-invalid={invalido || undefined}
                  aria-describedby={invalido ? `${id}-erro` : undefined}
                >
                  <legend>
                    {index + 1}. {texto}
                  </legend>
                  {OPCOES_FREQUENCIA.map((opcao) => (
                    <label key={opcao.value} className="checkbox">
                      <input
                        type="radio"
                        name={id}
                        value={opcao.value}
                        checked={valor === opcao.value}
                        onChange={() => responder(instrumento, index, opcao.value)}
                      />
                      {opcao.label}
                    </label>
                  ))}
                  {invalido && (
                    <p id={`${id}-erro`} className="field-error">
                      <span aria-hidden="true">⚠ </span>
                      Responda esta pergunta.
                    </p>
                  )}
                </fieldset>
              )
            })}
          </section>
        ))}

        <p className="muted">
          O Sintoniza não acompanha suas respostas em tempo real e não avisa ninguém.
        </p>

        {tentouConcluir && pendentes.length > 0 && (
          <div role="alert" className="field-error">
            <p>Responda a todas as perguntas para concluir a avaliação. Faltam:</p>
            <ul>
              {pendentes.map(({ instrumento, index }) => (
                <li key={itemId(instrumento, index)}>
                  <a href={`#${itemId(instrumento, index)}`}>
                    {instrumento.title}, pergunta {index + 1}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {error && <p role="alert">{error}</p>}

        <div className="avaliacao-acoes">
          <button type="submit" className="button button-primary" disabled={submitting}>
            {submitting ? 'Enviando…' : 'Concluir avaliação'}
          </button>
          <Link to="/">Cancelar</Link>
        </div>
      </form>
    </section>
  )
}
