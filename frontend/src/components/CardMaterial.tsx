import type { Recomendacao } from '../api/recomendacoes'

interface CardMaterialProps {
  recomendacao: Recomendacao
}

/**
 * Material recomendado: título, fonte e resumo do catálogo, link para a página oficial em nova aba
 * (Visão, seção 4.5.4) e o motivo em "Por que estou vendo isto?" (R-S5; vocabulário, Quadro 10).
 */
export function CardMaterial({ recomendacao }: CardMaterialProps) {
  const { titulo, fonte, resumo, url, motivo } = recomendacao
  return (
    <article className="material-card">
      <h3>{titulo}</h3>
      <p className="material-fonte">Fonte: {fonte}</p>
      <p>{resumo}</p>
      <a href={url} target="_blank" rel="noopener noreferrer">
        Abrir no site oficial
        <span className="visually-hidden">: {titulo} (abre em nova aba)</span>
      </a>
      <details className="material-motivo">
        <summary>Por que estou vendo isto?</summary>
        <p>{motivo}</p>
      </details>
    </article>
  )
}
