
import { useEffect, useState } from 'react'
import { mockCheckins } from '../mocks/checkins'
import type { Checkin } from '../api/checkins'

const dateFormatter = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'long',
})

const tagLabels: Record<string, string> = {
  humor: 'Humor',
  ansiedade: 'Ansiedade',
  sono: 'Sono',
  estresse: 'Estresse',
  bem_estar: 'Bem-estar',
  ajuda_profissional: 'Ajuda profissional',
}

function formatDate(value: string) {
  const [year, month, day] = value.split('-').map(Number)

  return dateFormatter.format(new Date(year, month - 1, day))
}

function groupByDate(checkins: Checkin[]) {
  return checkins.reduce<Record<string, Checkin[]>>((groups, checkin) => {
    if (!groups[checkin.data]) {
      groups[checkin.data] = []
    }

    groups[checkin.data].push(checkin)

    return groups
  }, {})
}

export function HistoryPage() {
  const [checkins, setCheckins] = useState<Checkin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    // Simula o tempo de resposta de uma API.
    const timeout = setTimeout(() => {
      setCheckins(mockCheckins)
      setLoading(false)
    }, 500)

    return () => clearTimeout(timeout)
  }, [])

  const groupedCheckins = groupByDate(checkins)

  const dates = Object.keys(groupedCheckins).sort((a, b) =>
    b.localeCompare(a),
  )

  if (loading) {
    return (
      <section className="card" aria-labelledby="history-title">
        <h1 id="history-title">Histórico de check-ins</h1>
        <p role="status">Carregando histórico...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="card" aria-labelledby="history-title">
        <h1 id="history-title">Histórico de check-ins</h1>
        <p role="alert">
          Não foi possível carregar o histórico. Tente novamente.
        </p>
      </section>
    )
  }

  return (
    <section className="card" aria-labelledby="history-title">
      <h1 id="history-title">Histórico de check-ins</h1>

      {checkins.length === 0 ? (
        <p className="muted">
          Você ainda não possui check-ins registrados.
        </p>
      ) : (
        dates.map((date) => (
          <section key={date} aria-labelledby={`date-${date}`}>
            <h2 id={`date-${date}`}>{formatDate(date)}</h2>

            {groupedCheckins[date].map((checkin) => (
              <article key={checkin.id}>
                <p>
                  <strong>Humor:</strong>{' '}
                  {checkin.humor ?? 'Não informado'}
                </p>

                {checkin.tags.length > 0 && (
                  <p>
                    <strong>Temas:</strong>{' '}
                    {checkin.tags
                      .map((tag) => tagLabels[tag] ?? tag)
                      .join(', ')}
                  </p>
                )}
              </article>
            ))}
          </section>
        ))
      )}
    </section>
  )
}
