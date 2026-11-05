/**
 * Constantes do check-in diário.
 *
 * As perguntas e escalas foram extraídas do Quadro 15
 * do documento de Visão do Produto.
 *
 * As regras de classificação seguem o Quadro 16.
 */

export const CHECKIN_QUESTIONS = [
  {
    id: 'p1',
    code: 'P1',
    question: 'Como você está se sentindo hoje?',
    type: 'scale',
    min: 1,
    max: 5,
    options: [
      { value: 1, label: 'Muito ruim' },
      { value: 2, label: 'Ruim' },
      { value: 3, label: 'Regular' },
      { value: 4, label: 'Bom' },
      { value: 5, label: 'Muito bom' },
    ],
    required: false,
  },
  {
    id: 'p2',
    code: 'P2',
    question: 'Quanto você se sentiu ansioso(a) hoje?',
    type: 'scale',
    min: 0,
    max: 3,
    options: [
      { value: 0, label: 'Nada' },
      { value: 1, label: 'Um pouco' },
      { value: 2, label: 'Bastante' },
      { value: 3, label: 'Extremamente' },
    ],
    required: false,
  },
  {
    id: 'p3',
    code: 'P3',
    question: 'Como foi a qualidade do seu sono?',
    type: 'scale',
    min: 1,
    max: 5,
    options: [
      { value: 1, label: 'Muito ruim' },
      { value: 2, label: 'Ruim' },
      { value: 3, label: 'Regular' },
      { value: 4, label: 'Bom' },
      { value: 5, label: 'Muito bom' },
    ],
    required: false,
  },
  {
    id: 'p4',
    code: 'P4',
    question: 'Quanto você se sentiu sobrecarregado(a) hoje?',
    type: 'scale',
    min: 0,
    max: 3,
    options: [
      { value: 0, label: 'Nada' },
      { value: 1, label: 'Um pouco' },
      { value: 2, label: 'Bastante' },
      { value: 3, label: 'Extremamente' },
    ],
    required: false,
  },
  {
    id: 'p5',
    code: 'P5',
    question: 'Você teve pensamentos de se machucar ou de que seria melhor não estar vivo(a)?',
    type: 'boolean',
    options: [
      { value: false, label: 'Não' },
      { value: true, label: 'Sim' },
    ],
    required: true,
  },
] as const

/**
 * Tags utilizadas para representar os resultados
 * e possíveis recomendações do check-in.
 */
export const CHECKIN_TAGS = {
  HUMOR: 'HUMOR',
  ANSIEDADE: 'ANSIEDADE',
  SONO: 'SONO',
  ESTRESSE: 'ESTRESSE',
  BEM_ESTAR: 'BEM_ESTAR',
  AJUDA_PROFISSIONAL: 'AJUDA_PROFISSIONAL',
} as const

/**
 * Rótulos apresentados ao usuário para cada tag.
 */
export const CHECKIN_TAG_LABELS = {
  [CHECKIN_TAGS.HUMOR]: 'Humor',
  [CHECKIN_TAGS.ANSIEDADE]: 'Ansiedade',
  [CHECKIN_TAGS.SONO]: 'Sono',
  [CHECKIN_TAGS.ESTRESSE]: 'Estresse',
  [CHECKIN_TAGS.BEM_ESTAR]: 'Bem-estar',
  [CHECKIN_TAGS.AJUDA_PROFISSIONAL]: 'Ajuda profissional',
} as const

/**
 * Regras para identificar possíveis sinais de atenção.
 *
 * Os valores indicam condições para classificação,
 * não diagnósticos clínicos.
 */
export const CHECKIN_RULES = {
  [CHECKIN_TAGS.HUMOR]: {
    field: 'p1',
    operator: '<=',
    value: 2,
  },
  [CHECKIN_TAGS.ANSIEDADE]: {
    field: 'p2',
    operator: '>=',
    value: 2,
  },
  [CHECKIN_TAGS.SONO]: {
    field: 'p3',
    operator: '<=',
    value: 2,
  },
  [CHECKIN_TAGS.ESTRESSE]: {
    field: 'p4',
    operator: '>=',
    value: 2,
  },
} as const

/**
 * Tipos derivados das constantes.
 */
export type CheckinQuestion = (typeof CHECKIN_QUESTIONS)[number]

export type CheckinQuestionId = CheckinQuestion['id']

export type CheckinTag = (typeof CHECKIN_TAGS)[keyof typeof CHECKIN_TAGS]
