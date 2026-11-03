import { useState, type FormEvent } from 'react';
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router';
import { CHECKIN_QUESTIONS, type CheckinQuestion } from '../constants/checkin';

type AnswerValue = number | boolean
type Option = { readonly value: AnswerValue; readonly label: string }

const getOptions = (q: CheckinQuestion) => q.options as readonly Option[]

const dateFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' })

function CheckinDiario() {}


export function DailyCheckin() {
  const { user } = useAuth()
  if (!user) return null

  const navigate = useNavigate()
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSubmit = CHECKIN_QUESTIONS.every(
    (q) => !q.required || answers[q.id] !== undefined,
  )

  function handleChange(q: CheckinQuestion, raw: string) {
    setAnswers((prev) => {
      const next = { ...prev }
      const option = getOptions(q).find((o) => String(o.value) === raw)
      if (option) next[q.id] = option.value
      else delete next[q.id]
      return next
    })
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!canSubmit || submitting) return

    const payload = CHECKIN_QUESTIONS.filter((q) => answers[q.id] !== undefined).map(
      (q) => ({
        question_id: q.id,
        code: q.code,
        answer: answers[q.id],
      }),
    )

    setSubmitting(true)
    setError(null)

    try {
      const res = await fetch('/api/checkin', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: payload }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      navigate('/', { replace: true })
    } catch {
      setError('Não foi possível enviar o check-in. Tente novamente.')
      setSubmitting(false)
    }
  }



  return (
    <section className="card" aria-labelledby="home-title">
      <h1 id="home-title">Check-in diário</h1>
      <p>
        Você está conectado como <strong>{user.email}</strong>.
      </p>

      <form onSubmit={handleSubmit}>
        {CHECKIN_QUESTIONS.map((q) => {
          const current = answers[q.id]
          return (
            <div key={q.id} className="field">
              <label htmlFor={`q-${q.id}`}>
                {q.question}
                {q.required && ' *'}
              </label>
              <select
                id={`q-${q.id}`}
                name={q.code}
                value={current === undefined ? '' : String(current)}
                onChange={(e) => handleChange(q, e.target.value)}
                required={q.required}
                aria-required={q.required}
              >
                <option value="" disabled={q.required}>
                  {q.required ? 'Selecione...' : 'Selecione (opcional)'}
                </option>
                {getOptions(q).map((opt) => (
                  <option key={String(opt.value)} value={String(opt.value)}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          )
        })}

        {error && <p role="alert">{error}</p>}

        <button
          type="submit"
          className="button button-primary"
          disabled={!canSubmit || submitting}
        >
          {submitting ? 'Enviando...' : 'Enviar check-in'}
        </button>
      </form>
    

    </section>
  )
}
