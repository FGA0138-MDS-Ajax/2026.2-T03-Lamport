import { useEffect, useRef } from 'react'
import { Link } from 'react-router'
import type { Recomendacao } from '../api/recomendacoes'
import { Alert } from './Alert'
import { CardMaterial } from './CardMaterial'

interface ConteudosDoDiaProps {
  recomendacoes: Recomendacao[]
  /** `true` logo após o envio; `false` ao reabrir o check-in já feito no dia. */
  acabouDeRegistrar: boolean
}

/** Resultado do check-in sem risco (vocabulário do check-in, Quadro 10; Arquitetura, Figura 3). */
export function ConteudosDoDia({ recomendacoes, acabouDeRegistrar }: ConteudosDoDiaProps) {
  const titleRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    titleRef.current?.focus()
  }, [])

  return (
    <section className="card" aria-labelledby="conteudos-title">
      {acabouDeRegistrar ? (
        <Alert tone="success">Check-in de hoje registrado.</Alert>
      ) : (
        <p className="muted">
          Você já fez o check-in de hoje. Um novo check-in fica disponível amanhã.
        </p>
      )}

      <h1 id="conteudos-title" ref={titleRef} tabIndex={-1}>
        Conteúdos para hoje
      </h1>

      {recomendacoes.length > 0 ? (
        <>
          <p>Separamos materiais de fontes oficiais com base nas suas respostas.</p>
          <ul className="material-list">
            {recomendacoes.map((recomendacao) => (
              <li key={`${recomendacao.regra}-${recomendacao.url}`}>
                <CardMaterial recomendacao={recomendacao} />
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p>Não encontramos materiais para hoje. Continue acompanhando como você está.</p>
      )}

      <p className="muted">
        O check-in não é um teste de saúde: ele serve apenas para sugerir conteúdos de autocuidado.
      </p>

      <nav className="result-nav" aria-label="Depois do check-in">
        <Link to="/historico">Ver histórico</Link>
        <Link to="/">Voltar ao início</Link>
      </nav>
    </section>
  )
}
