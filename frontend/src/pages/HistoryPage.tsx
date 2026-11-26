import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/AuthContext'
import { avaliacoesApi, type AvaliacaoListItem } from '../api/avaliacoes'
import { checkinsApi, type Checkin } from '../api/checkins'
import { faixaLabels, nivelLabels } from '../constants/avaliacao'
import { useNavigate } from 'react-router'


function CheckinButton() {
  const navigate = useNavigate()
  const handleCheckin = () => {
    navigate('/DailyCheckin')
  }

  return (
    <button type="button" className="button button-primary" onClick={handleCheckin}>
      {'Fazer o primeiro check-in'}
    </button>
  )
}

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

interface ListState<T> {
  items: T[]
  loading: boolean
  error: boolean
}


function useList<T>(token: string | null, load: (token: string) => Promise<T[]>): ListState<T> {
  const [state, setState] = useState<ListState<T>>({ items: [], loading: true, error: false })

  useEffect(() => {
    let cancelled = false

    async function run() {
      if (!token) {
        setState({ items: [], loading: false, error: true })
        return
      }

      try {
        const items = await load(token)
        if (!cancelled) setState({ items, loading: false, error: false })
      } catch {
        if (!cancelled) setState({ items: [], loading: false, error: true })
      }
    }

    void run()

    return () => {
      cancelled = true
    }
  }, [token, load])

  return state
}

const loadCheckins = (token: string) => checkinsApi.listCheckins(token, 30)
const loadAvaliacoes = (token: string) => avaliacoesApi.listAvaliacoes(token)

function CheckinsSection({ token }: { token: string | null }) {
  const { items: checkins, loading, error } = useList<Checkin>(token, loadCheckins)

  return (
    <section className="history-section" aria-labelledby="history-checkins-title">
      <h2 id="history-checkins-title">Check-ins</h2>

      {loading ? (
        <p className="muted" role="status">
          Carregando histórico...
        </p>
      ) : error ? (
        <p role="alert">Não foi possível carregar o histórico. Tente novamente.</p>
      ) : (
        <>
          <p className="muted history-description">Seus últimos 30 check-ins.</p>

          {checkins.length === 0 ? (
            <div className="history-empty">
              <p>Você ainda não fez nenhum check-in.</p>
              <CheckinButton />
            </div>
          ) : (
            <div className="history-list">
              {checkins.map((checkin) => (
                <article className="history-item" key={checkin.id}>
                  <strong className="history-date">{formatDate(checkin.data)}</strong>

                  <div className="history-details">
                    <p className="history-humor">
                      <strong>Humor:</strong>{' '}
                      {checkin.p1 === null
                        ? 'Não informado'
                        : (humorLabels[checkin.p1] ?? 'Não informado')}
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
        </>
      )}
    </section>
  )
}

function AvaliacoesSection({ token }: { token: string | null }) {
  const { items: avaliacoes, loading, error } = useList<AvaliacaoListItem>(token, loadAvaliacoes)

  return (
    <section className="history-section" aria-labelledby="history-avaliacoes-title">
      <h2 id="history-avaliacoes-title">Avaliações</h2>

      {loading ? (
        <p className="muted" role="status">
          Carregando avaliações...
        </p>
      ) : error ? (
        <p role="alert">Não foi possível carregar as avaliações. Tente novamente.</p>
      ) : avaliacoes.length === 0 ? (
        <div className="history-empty">
          <p>Você ainda não fez nenhuma avaliação.</p>
        </div>
      ) : (
        <div className="history-list">
          {avaliacoes.map((avaliacao) => (
            <Link
              className="history-item history-item-link"
              key={avaliacao.id}
              to={`/avaliacoes/${avaliacao.id}`}
            >
              <strong className="history-date">{formatDate(avaliacao.data)}</strong>

              <div className="history-details">
                <p className="history-score">
                  <strong>PHQ-9:</strong> {avaliacao.escore_phq9} ·{' '}
                  {faixaLabels[avaliacao.faixa_phq9]}
                </p>
                <p className="history-score">
                  <strong>GAD-7:</strong> {avaliacao.escore_gad7} ·{' '}
                  {faixaLabels[avaliacao.faixa_gad7]}
                </p>
                <p className="history-score">
                  <strong>Nível:</strong> {nivelLabels[avaliacao.nivel]}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  )
}

export function HistoryPage() {
  const { token } = useAuth()

  return (
    <section className="history-page" aria-labelledby="history-title">
      <h1 id="history-title">Histórico</h1>
      <CheckinsSection token={token} />
      <AvaliacoesSection token={token} />
    </section>
  )
}
