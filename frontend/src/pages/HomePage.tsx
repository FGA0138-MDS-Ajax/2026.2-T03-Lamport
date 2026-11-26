import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router'
import { BiweeklyAssesment } from './BiweeklyAssesment'
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

function BiweeklyAssesmentButton() {
  const navigate = useNavigate()
  const handleBiweeklyAssesment = () => {
    navigate('/BiweeklyAssesment')
  }

  return (
    <button type="button" className="button button-primary" onClick={handleBiweeklyAssesment}>
      {'Avaliação Quinzenal'}
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

      <CheckinButton />
      
      <div style={{ height: "20px" }} />
      <p className="muted">
        A cada 15 dias, você será convidado a preencher uma avaliação quinzenal. Ela é opcional, mas
        ajuda a monitorar seu bem-estar.
      </p>
      <BiweeklyAssesmentButton />

      <ExcluirConta />
    </section>
  )
}
