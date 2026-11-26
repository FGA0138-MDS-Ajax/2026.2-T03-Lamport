import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router'
import { ExcluirConta } from '../components/ExcluirConta'

const dateFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' })

function CheckinButton() {
  const navigate = useNavigate()
  const handleCheckin = () => {
    navigate('/DailyCheckin')
  }

  return (
    <button type="button" className="button button-primary" onClick={handleCheckin}>
      {'Check-in Diário'}
    </button>
  )
}

function AvaliacaoButton() {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      className="button button-primary"
      onClick={() => navigate('/avaliacoes/nova')}
    >
      Avaliação quinzenal
    </button>
  )
}

export function HomePage() {
  const { user } = useAuth()

  if (!user) return null

  return (
    <section className="card" aria-labelledby="home-title">
      <h1 id="home-title">Olá!</h1>
      <p>
        Você está conectado como <strong>{user.email}</strong>.
      </p>
      <p className="muted">Conta criada em {dateFormatter.format(new Date(user.criado_em))}.</p>

      <div className="home-acoes">
        <CheckinButton />
        <AvaliacaoButton />
      </div>

      <ExcluirConta />
    </section>
  )
}
