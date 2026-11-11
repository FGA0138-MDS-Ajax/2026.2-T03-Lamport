import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useLocation, useNavigate } from 'react-router'
import { Alert } from '../components/Alert'

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

function CheckinAlreadyExistsAlert() {
  return <Alert tone="error">Você já realizou o check-in hoje.</Alert>
}

export function HomePage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [checkinAlreadyExists] = useState(Boolean(location.state?.checkinAlreadyExists))

  useEffect(() => {
    if (location.state?.checkinAlreadyExists) {
      navigate(location.pathname, { replace: true, state: null })
    }
  }, [location.state, location.pathname, navigate])

  if (!user) return null

  return (
    <section className="card" aria-labelledby="home-title">
      <h1 id="home-title">Olá!</h1>
      <p>
        Você está conectado como <strong>{user.email}</strong>.
      </p>
      <p className="muted">Conta criada em {dateFormatter.format(new Date(user.criado_em))}.</p>

      {checkinAlreadyExists && <CheckinAlreadyExistsAlert />}

      <CheckinButton />
    </section>
  )
}
