import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section className="card" aria-labelledby="not-found-title">
      <h1 id="not-found-title">Página não encontrada</h1>
      <p className="muted">O endereço acessado não existe.</p>
      <Link to="/">Voltar ao início</Link>
    </section>
  )
}
