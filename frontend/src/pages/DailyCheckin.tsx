import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router'
import { CHECKIN_QUESTIONS, type CheckinQuestion } from '../constants/checkin'
import { checkinsApi } from '../api/checkins'
import { ApiError } from '../api/client'

type AnswerValue = number | boolean
type Option = { readonly value: AnswerValue; readonly label: string }

const getOptions = (q: CheckinQuestion) => q.options as readonly Option[]

export interface CreateCheckinData {
  p1: number | null
  p2: number | null
  p3: number | null
  p4: number | null
  p5: boolean
}

export function DailyCheckin() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Se já existe check-in hoje, volta para a home avisando o usuário.
  useEffect(() => {
    if (!token) return
    let cancelled = false
    checkinsApi
      .getTodayCheckin(token)
      .then((today) => {
        if (!cancelled && today != null) {
          navigate('/', { state: { checkinAlreadyExists: true } })
        }
      })
      .catch((err) => {
        if (err instanceof ApiError) console.error('Erro ao verificar o check-in de hoje:', err)
      })
    return () => {
      cancelled = true
    }
  }, [token, navigate])

  if (!user) return null

  const canSubmit = CHECKIN_QUESTIONS.every((q) => !q.required || answers[q.id] !== undefined)

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

    const payload = CHECKIN_QUESTIONS.filter((q) => answers[q.id] !== undefined).map((q) => ({
      question_id: q.id,
      code: q.code,
      answer: answers[q.id],
    }))

    setSubmitting(true)
    setError(null)

    const checkinData: CreateCheckinData = {
      p1: (payload.find((p) => p.question_id === 'p1')?.answer as number | null) ?? null,
      p2: (payload.find((p) => p.question_id === 'p2')?.answer as number | null) ?? null,
      p3: (payload.find((p) => p.question_id === 'p3')?.answer as number | null) ?? null,
      p4: (payload.find((p) => p.question_id === 'p4')?.answer as number | null) ?? null,
      p5: payload.find((p) => p.question_id === 'p5')?.answer as boolean,
    }

    const hasRisk = checkinData.p5 === true
    try {
      await checkinsApi.createCheckin(token as string, checkinData)
      navigate(hasRisk ? '/risco' : '/')
    } catch {
      setError('Não foi possível enviar o check-in. Tente novamente.')
      setSubmitting(false)
      // Por segurança, sinal de risco leva à página de ajuda mesmo se o envio falhar.
      if (hasRisk) navigate('/risco')
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

        <button type="submit" className="button button-primary" disabled={!canSubmit || submitting}>
          {submitting ? 'Enviando...' : 'Enviar check-in'}
        </button>
      </form>
    </section>
  )
}
