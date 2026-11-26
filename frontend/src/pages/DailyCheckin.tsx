import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router'
import { CHECKIN_QUESTIONS, type CheckinQuestion } from '../constants/checkin'
import { checkinsApi, type CheckinResultado } from '../api/checkins'
import { ApiError } from '../api/client'
import type { Recomendacao } from '../api/recomendacoes'
import { AJUDA_PATH } from '../constants/ajuda'
import { ConteudosDoDia } from '../components/ConteudosDoDia'
import { LoadingState } from '../components/LoadingState'

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

interface Resultado {
  recomendacoes: Recomendacao[]
  acabouDeRegistrar: boolean
}

export function DailyCheckin() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [checkingToday, setCheckingToday] = useState(true)
  const [resultado, setResultado] = useState<Resultado | null>(null)

  // Resultado já registrado do dia (Arquitetura, Figura 3; vocabulário, Quadro 7):
  // nível crise abre a Tela de Ajuda; os demais mostram os materiais gravados.
  function showResult(checkin: CheckinResultado, acabouDeRegistrar: boolean) {
    if (checkin.nivel === 'crise') {
      navigate(AJUDA_PATH, { replace: !acabouDeRegistrar })
      return
    }
    setResultado({ recomendacoes: checkin.recomendacoes, acabouDeRegistrar })
  }

  useEffect(() => {
    if (!token) return
    let cancelled = false
    checkinsApi
      .getTodayCheckin(token)
      .then((today) => {
        if (cancelled) return
        if (today.nivel === 'crise') navigate(AJUDA_PATH, { replace: true })
        else setResultado({ recomendacoes: today.recomendacoes, acabouDeRegistrar: false })
      })
      .catch((err) => {
        // 404: ainda não há check-in hoje, então o formulário é exibido.
        if (err instanceof ApiError && err.status !== 404) {
          console.error('Erro ao verificar o check-in de hoje:', err)
        }
      })
      .finally(() => {
        if (!cancelled) setCheckingToday(false)
      })
    return () => {
      cancelled = true
    }
  }, [token, navigate])

  if (!user) return null
  if (checkingToday) return <LoadingState />
  if (resultado) {
    return (
      <ConteudosDoDia
        recomendacoes={resultado.recomendacoes}
        acabouDeRegistrar={resultado.acabouDeRegistrar}
      />
    )
  }

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
      const created = await checkinsApi.createCheckin(token as string, checkinData)
      if (hasRisk) navigate(AJUDA_PATH)
      else showResult(created, true)
    } catch (err) {
      // Por segurança, sinal de risco leva à página de ajuda mesmo se o envio falhar.
      if (hasRisk) {
        navigate(AJUDA_PATH)
        return
      }
      // 409: o check-in de hoje já existe; mostra o resultado do dia (vocabulário, Quadro 13).
      if (err instanceof ApiError && err.status === 409) {
        try {
          showResult(await checkinsApi.getTodayCheckin(token as string), false)
          return
        } catch {
          // Segue para a mensagem de erro abaixo.
        }
      }
      setError('Não foi possível enviar o check-in. Tente novamente.')
      setSubmitting(false)
    }
  }

  return (
    <section className="card" aria-labelledby="checkin-title">
      <h1 id="checkin-title">Check-in diário</h1>
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
