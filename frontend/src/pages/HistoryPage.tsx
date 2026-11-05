
import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { checkinsApi, type Checkin } from '../api/checkins'

const tagLabels: Record<string, string> = {
  HUMOR: 'Humor',
  ANSIEDADE: 'Ansiedade',
  SONO: 'Sono',
  ESTRESSE: 'Estresse',
  BEM_ESTAR: 'Bem-estar',
  AJUDA_PROFISSIONAL: 'Ajuda profissional',
}

const humorLabels: Record<number, string> = {
  1: 'Muito ruim',
  2: 'Ruim',
  3: 'Regular',
  4: 'Bom',
  5: 'Muito bom',
}

function formatDate(value: string) {
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(year, month - 1, day)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.getTime() === today.getTime()) return 'Hoje'
  if (date.getTime() === yesterday.getTime()) return 'Ontem'

  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
  })
    .format(date)
    .replace('.', '')
}

export function HistoryPage() {
  const { token } = useAuth()

  const [checkins, setCheckins] = useState<Checkin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadCheckins() {
      if (!token) {
        setError(true)
        setLoading(false)
        return
      }

      try {
        const response = await checkinsApi.listCheckins(token, 30)

        if (!cancelled) {
          setCheckins(response)
          setError(false)
        }
      } catch {
        if (!cancelled) {
          setError(true)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadCheckins()

    return () => {
      cancelled = true
    }
  }, [token])

  if (loading) {
    return (
      <section className="history-page" aria-labelledby="history-title">
        <h1 id="history-title">Histórico</h1>
        <p className="muted" role="status">
          Carregando histórico...
        </p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="history-page" aria-labelledby="history-title">
        <h1 id="history-title">Histórico</h1>
        <p role="alert">
          Não foi possível carregar o histórico. Tente novamente.
        </p>
      </section>
    )
  }

  return (
    <section className="history-page" aria-labelledby="history-title">
      <h1 id="history-title">Histórico</h1>
      <p className="muted history-description">
        Seus últimos 30 check-ins.
      </p>

      {checkins.length === 0 ? (
        <div className="history-empty">
          <p>Você ainda não fez nenhum check-in.</p>
          <button
            type="button"
            className="button button-primary history-empty-button"
          >
            Fazer o primeiro check-in
          </button>
        </div>
      ) : (
        <div className="history-list">
          {checkins.map((checkin) => (
            <article className="history-item" key={checkin.id}>
              <strong className="history-date">
                {formatDate(checkin.data)}
              </strong>

              <div className="history-details">
                <p className="history-humor">
                  <strong>Humor:</strong>{' '}
                  {checkin.p1 === null
                    ? 'Não informado'
                    : humorLabels[checkin.p1] ?? 'Não informado'}
                </p>

                {checkin.tags.length > 0 && (
                  <div className="history-tags">
                    <span className="history-tags-label">Temas:</span>

                    <div className="history-tag-list">
                      {checkin.tags.map((tag) => (
                        <span className="history-tag" key={tag}>
                          {tagLabels[tag] ?? tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
