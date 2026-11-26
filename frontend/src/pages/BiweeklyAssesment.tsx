import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router'
import { BWASSESMENT_QUESTIONS, type BWAssesmmentQuestion } from '../constants/bwassesment'
import { checkinsApi } from '../api/checkins'
import { ApiError } from '../api/client'
import { AJUDA_PATH } from '../constants/ajuda'
import { avaliacoesApi, type CreateAvaliacaoData } from '../api/avaliacoes'

type AnswerValue = number | boolean
type Option = { readonly value: AnswerValue; readonly label: string }

const getOptions = (q: BWAssesmmentQuestion) => q.options as readonly Option[]

export interface CreateAssesmentData {
  phq9_q1: number | null
  phq9_q2: number | null
  phq9_q3: number | null
  phq9_q4: number | null
  phq9_q5: number | null
  phq9_q6: number | null
  phq9_q7: number | null
  phq9_q8: number | null
  phq9_q9: number
  gad7_q1: number | null
  gad7_q2: number | null
  gad7_q3: number | null
  gad7_q4: number | null
  gad7_q5: number | null
  gad7_q6: number | null
  gad7_q7: number | null
}

export function BiweeklyAssesment() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Se já existe check-in hoje, volta para a home avisando o usuário.
  /*useEffect(() => {
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
  }, [token, navigate])*/

  if (!user) return null

  const canSubmit = BWASSESMENT_QUESTIONS.every((q) => !q.required || answers[q.id] !== undefined)

  function handleChange(q: BWAssesmmentQuestion, raw: string) {
    setAnswers((prev) => {
      const next = { ...prev }
      const option = getOptions(q).find((o) => String(o.value) === raw)
      if (option) next[q.id] = option.value
      else delete next[q.id]
      return next
    })
  }

  function createAssesmentDataFromAnswers(data: CreateAssesmentData): CreateAvaliacaoData {
    const AvaliacaoData: CreateAvaliacaoData = {
        phq9: [
            data.phq9_q1 ?? 0,
            data.phq9_q2 ?? 0,
            data.phq9_q3 ?? 0,
            data.phq9_q4 ?? 0,
            data.phq9_q5 ?? 0,
            data.phq9_q6 ?? 0,
            data.phq9_q7 ?? 0,
            data.phq9_q8 ?? 0,
            data.phq9_q9 ?? 0,
        ],
        gad7: [
            data.gad7_q1 ?? 0,
            data.gad7_q2 ?? 0,
            data.gad7_q3 ?? 0,
            data.gad7_q4 ?? 0,
            data.gad7_q5 ?? 0,
            data.gad7_q6 ?? 0,
            data.gad7_q7 ?? 0,
        ],
    }

    return AvaliacaoData
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!canSubmit || submitting) return

    const payload = BWASSESMENT_QUESTIONS.filter((q) => answers[q.id] !== undefined).map((q) => ({
      question_id: q.id,
      code: q.code,
      answer: answers[q.id],
    }))

    setSubmitting(true)
    setError(null)

    const AssesmentData: CreateAssesmentData = {
      phq9_q1: (payload.find((p) => p.question_id === 'phq9_q1')?.answer as number | null) ?? null,
      phq9_q2: (payload.find((p) => p.question_id === 'phq9_q2')?.answer as number | null) ?? null,
      phq9_q3: (payload.find((p) => p.question_id === 'phq9_q3')?.answer as number | null) ?? null,
      phq9_q4: (payload.find((p) => p.question_id === 'phq9_q4')?.answer as number | null) ?? null,
      phq9_q5: (payload.find((p) => p.question_id === 'phq9_q5')?.answer as number | null) ?? null,
      phq9_q6: (payload.find((p) => p.question_id === 'phq9_q6')?.answer as number | null) ?? null,
      phq9_q7: (payload.find((p) => p.question_id === 'phq9_q7')?.answer as number | null) ?? null,
      phq9_q8: (payload.find((p) => p.question_id === 'phq9_q8')?.answer as number | null) ?? null,
      phq9_q9: (payload.find((p) => p.question_id === 'phq9_q9')?.answer as number),
      gad7_q1: (payload.find((p) => p.question_id === 'gad7_q1')?.answer as number | null) ?? null,
      gad7_q2: (payload.find((p) => p.question_id === 'gad7_q2')?.answer as number | null) ?? null,
      gad7_q3: (payload.find((p) => p.question_id === 'gad7_q3')?.answer as number | null) ?? null,
      gad7_q4: (payload.find((p) => p.question_id === 'gad7_q4')?.answer as number | null) ?? null,
      gad7_q5: (payload.find((p) => p.question_id === 'gad7_q5')?.answer as number | null) ?? null,
      gad7_q6: (payload.find((p) => p.question_id === 'gad7_q6')?.answer as number | null) ?? null,
      gad7_q7: (payload.find((p) => p.question_id === 'gad7_q7')?.answer as number | null) ?? null,
    }

    const hasRisk = AssesmentData.phq9_q9 >= 1;
    try {
      await avaliacoesApi.createAvaliacao(token as string, createAssesmentDataFromAnswers(AssesmentData))
      navigate(hasRisk ? AJUDA_PATH : '/')
    } catch {
      setError('Não foi possível enviar o check-in. Tente novamente.')
      setSubmitting(false)
      // Por segurança, sinal de risco leva à página de ajuda mesmo se o envio falhar.
      if (hasRisk) navigate(AJUDA_PATH)
    }
  }

  return (
    <section className="card" aria-labelledby="checkin-title">
      <h1 id="checkin-title">Avaliação quinzenal</h1>

      <p>
        Durante as últimas 2 semanas, com que freqüência você foi incomodado/a por qualquer um dos problemas abaixo?
      </p>

      <form onSubmit={handleSubmit}>
        {BWASSESMENT_QUESTIONS.map((q) => {
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
