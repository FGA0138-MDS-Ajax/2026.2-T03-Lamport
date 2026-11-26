import type { Faixa } from '../api/avaliacoes'
import type { Nivel } from '../api/checkins'

export const faixaLabels: Record<Faixa, string> = {
  minima: 'Mínima',
  leve: 'Leve',
  moderada: 'Moderada',
  moderadamente_grave: 'Moderadamente grave',
  grave: 'Grave',
}

export const nivelLabels: Record<Nivel, string> = {
  autocuidado: 'Orientação de autocuidado',
  atencao: 'Procurar a UBS',
  prioritario: 'Atenção prioritária',
  crise: 'Ajuda imediata',
}
