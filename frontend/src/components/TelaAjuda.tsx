/**
 * Tela de Ajuda Imediata (Visão, seção 4.5.5).
 *
 * O conteúdo é fixo e não depende da API, para funcionar mesmo com o backend fora do ar
 * (Arquitetura, seção 2.4, item 3). Não importe nada de `api/` neste componente.
 */
export function TelaAjuda() {
  return (
    <div className="tela-ajuda">
      <section className="card-alert" aria-labelledby="ajuda-title">
        <h1 id="ajuda-title" className="red-text">
          Ajuda Imediata
        </h1>
      </section>

      <section className="card" aria-labelledby="ajuda-cvv-title">
        <h2 id="ajuda-cvv-title">CVV – Centro de Valorização da Vida</h2>
        <p>
          Ligue <strong>188</strong>, gratuito, 24 horas por dia.
        </p>
        <a className="button button-primary button-link" href="tel:188">
          Ligue 188
        </a>
        <p>
          <a href="https://cvv.org.br/chat/" target="_blank" rel="noopener noreferrer">
            Atendimento por chat no site cvv.org.br
          </a>
        </p>
      </section>

      <section className="card" aria-labelledby="ajuda-samu-title">
        <h2 id="ajuda-samu-title">SAMU</h2>
        <p>
          Ligue <strong>192</strong>.
        </p>
        <a className="button button-primary button-link" href="tel:192">
          Ligue 192
        </a>
      </section>

      <div className="card prose">
        <ul>
          <li>Em perigo imediato, procure a UPA ou o pronto-socorro mais próximo.</li>
          <li>Procure alguém de confiança e não fique sozinho(a).</li>
        </ul>
      </div>

      <div className="card">
        <p className="muted">
          O Sintoniza não acompanha suas respostas em tempo real e não avisa ninguém. Se você
          precisa de ajuda agora, use os contatos acima.
        </p>
      </div>
    </div>
  )
}
