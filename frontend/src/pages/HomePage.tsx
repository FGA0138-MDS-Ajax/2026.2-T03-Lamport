import { useAuth } from '../auth/AuthContext'

const dateFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' })

export function HomePage() {
  const { user } = useAuth()
  if (!user) return null

  return (
    <section className="card" aria-labelledby="home-title">
      <h1 id="home-title">Olá!</h1>
      <p>
        Você está conectado como <strong>{user.email}</strong>.
      </p>
      <p className="muted">Conta criada em {dateFormatter.format(new Date(user.created_at))}.</p>
    </section>
  )
}
