/**
 * Recomendação devolvida pelas rotas de check-in e de avaliação, na ordem em que foi selecionada.
 * `titulo`, `fonte`, `resumo` e `url` vêm do Material; `regra` e `motivo`, da Recomendacao
 * (Arquitetura v2.5, seção 2.5.3 e Figura 6; Visão, R06 e R-S5).
 */
export interface Recomendacao {
  titulo: string
  fonte: string
  resumo: string
  url: string
  regra: string
  motivo: string
}
