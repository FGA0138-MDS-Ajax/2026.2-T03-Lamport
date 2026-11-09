import { Link } from 'react-router'

export function RiscoPage() {
  function handleCVV(): void {
    window.location.href = 'tel:188'
  }

  function handleSAMU(): void {
    window.location.href = 'tel:192'
  }

  return (
    <>
      <section className="card-alert" aria-labelledby="home-title">
        <h1 id="home-title" className="red-text">
          Ajuda Imediata
        </h1>
      </section>

      <section className="card" aria-labelledby="home-title">
        <h1 id="home-title">CVV - Centro de Valorização da Vida</h1>
        <p>Gratuito, 24 horas por dia.</p>
        <button type="button" className="button button-primary" onClick={handleCVV}>
          {'Ligue 188'}
        </button>
        <Link to="https://cvv.org.br/chat/">Atendimento por chat no site cvv.org.br</Link>
      </section>

      <section className="card" aria-labelledby="home-title">
        <h1 id="home-title">SAMU</h1>
        <button type="button" className="button button-primary" onClick={handleSAMU}>
          {'Ligue 192'}
        </button>
      </section>

      <section className="card" aria-labelledby="home-title">
        <p>• Em perigo imediato, procure a UPA ou o pronto-socorro mais próximo.</p>
        <p>• Procure alguém de confiança e não fique sozinho(a).</p>
      </section>

      <section className="card" aria-labelledby="home-title">
        <p className="muted">
          O Sintoniza não acompanha suas respostas em tempo real e não avisa ninguém. Se você
          precisa de ajuda agora, use os contatos acima.
        </p>
      </section>
    </>
  )
}
