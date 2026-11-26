import { Link } from 'react-router'
import type { Faixa, ResultadoAvaliacao as ResultadoAvaliacaoType } from '../api/avaliacoes'

interface ResultadoAvaliacaoProps {
  resultado: ResultadoAvaliacaoType
  recemRegistrada?: boolean
}

const faixaLabels: Record<Faixa, string> = {
  minima: 'Mínima',
  leve: 'Leve',
  moderada: 'Moderada',
  moderadamente_grave: 'Moderadamente grave',
  grave: 'Grave',
}

const nivelConfig = {
  autocuidado: {
    titulo: 'Orientação de autocuidado',
  },
  atencao: {
    titulo: 'Procurar a UBS',
  },
  prioritario: {
    titulo: 'Atenção prioritária',
  },
  crise: {
    titulo: 'Ajuda imediata',
  },
} as const

const faixasPhq9 = [
  { faixa: 'minima', label: 'Mínima', intervalo: '0–4' },
  { faixa: 'leve', label: 'Leve', intervalo: '5–9' },
  { faixa: 'moderada', label: 'Moderada', intervalo: '10–14' },
  {
    faixa: 'moderadamente_grave',
    label: 'Moderadamente grave',
    intervalo: '15–19',
  },
  { faixa: 'grave', label: 'Grave', intervalo: '20–27' },
] as const

const faixasGad7 = [
  { faixa: 'minima', label: 'Mínima', intervalo: '0–4' },
  { faixa: 'leve', label: 'Leve', intervalo: '5–9' },
  { faixa: 'moderada', label: 'Moderada', intervalo: '10–14' },
  { faixa: 'grave', label: 'Grave', intervalo: '15–21' },
] as const

function ScoreCard({
  titulo,
  descricao,
  escore,
  faixa,
  total,
  faixas,
}: {
  titulo: string
  descricao: string
  escore: number
  faixa: Faixa
  total: number
  faixas: ReadonlyArray<{
    faixa: Faixa
    label: string
    intervalo: string
  }>
}) {
  return (
    <article className="resultado-score">
      <header className="resultado-score-header">
        <div>
          <h3>{titulo}</h3>
          <p>{descricao}</p>
        </div>

        <p className="resultado-score-value">
          {escore}
          <span> de {total}</span>
        </p>
      </header>

      <p className="resultado-score-range">
        Faixa: <strong>{faixaLabels[faixa]}</strong>
      </p>

      <ul className="resultado-faixas" aria-label={`Escala ${titulo}`}>
        {faixas.map((item) => {
          const selecionada = item.faixa === faixa

          return (
            <li
              key={item.faixa}
              className={selecionada ? 'resultado-faixa resultado-faixa-ativa' : 'resultado-faixa'}
              aria-current={selecionada ? 'true' : undefined}
            >
              <span className="resultado-faixa-label">
                {item.label}
                {selecionada && <strong className="resultado-faixa-indicador">Sua faixa</strong>}
              </span>
              <span className="resultado-faixa-intervalo">{item.intervalo}</span>
            </li>
          )
        })}
      </ul>
    </article>
  )
}

export function ResultadoAvaliacao({
  resultado,
  recemRegistrada = false,
}: ResultadoAvaliacaoProps) {
  const config = nivelConfig[resultado.nivel]

  const recomendacoes = resultado.recomendacoes

  return (
    <section className="resultado-page" aria-labelledby="resultado-title">
      {recemRegistrada && (
        <div className="alert alert-success" role="status">
          <strong>Avaliação registrada.</strong>
        </div>
      )}

      <header className="resultado-header">
        <h1 id="resultado-title">Resultado da avaliação</h1>
      </header>

      <aside className="resultado-disclaimer" aria-label="Aviso importante">
        <strong>Este resultado não é um diagnóstico.</strong>
        <p>
          Ele resume suas respostas sobre as últimas duas semanas e não substitui a avaliação de um
          profissional de saúde.
        </p>
      </aside>

      <section className="resultado-orientacao" aria-labelledby="orientacao-title">
        <h2 id="orientacao-title">Orientação</h2>
        <h3>{config.titulo}</h3>
        <p>{resultado.orientacao}</p>
      </section>

      <section aria-labelledby="escores-title">
        <h2 id="escores-title">Seus escores</h2>

        <div className="resultado-scores">
          <ScoreCard
            titulo="PHQ-9"
            descricao="Sintomas de depressão"
            escore={resultado.escore_phq9}
            faixa={resultado.faixa_phq9}
            total={27}
            faixas={faixasPhq9}
          />

          <ScoreCard
            titulo="GAD-7"
            descricao="Sintomas de ansiedade"
            escore={resultado.escore_gad7}
            faixa={resultado.faixa_gad7}
            total={21}
            faixas={faixasGad7}
          />
        </div>

        <p className="resultado-score-note">
          O escore é a soma das respostas: de 0 a 27 pontos no PHQ-9 e de 0 a 21 pontos no GAD-7. As
          faixas são classificações dos instrumentos e não representam um diagnóstico.
        </p>
      </section>

      {resultado.nivel !== 'crise' && (
        <section aria-labelledby="recomendacoes-title">
          <h2 id="recomendacoes-title">Materiais recomendados</h2>

          <p className="resultado-section-description">
            Separamos materiais de fontes oficiais com base no seu resultado.
          </p>

          {recomendacoes.length === 0 ? (
            <p className="muted">Não há materiais recomendados para esta avaliação.</p>
          ) : (
            <div className="resultado-recomendacoes">
              {recomendacoes.map((recomendacao, index) => (
                <article className="resultado-material" key={`${recomendacao.url}-${index}`}>
                  <h3>{recomendacao.titulo}</h3>

                  <p className="resultado-material-source">Fonte: {recomendacao.fonte}</p>

                  <p className="resultado-material-summary">{recomendacao.resumo}</p>

                  <a href={recomendacao.url} target="_blank" rel="noopener noreferrer">
                    Abrir no site oficial ↗
                  </a>

                  <details className="resultado-material-reason" open>
                    <summary>Por que estou vendo isto?</summary>
                    <p>{recomendacao.motivo}</p>
                  </details>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      <nav className="resultado-actions" aria-label="Ações do resultado">
        <Link className="button button-secondary" to="/historico">
          Ver histórico
        </Link>

        <Link className="resultado-home-link" to="/">
          Voltar ao início
        </Link>
      </nav>
    </section>
  )
}
