// Textos oficiais do PHQ-9 e do GAD-7 (PHQ SCREENERS, 2026), com as mudanças do Quadro 7
// do vocabulário da avaliação (#52): um enunciado por instrumento, "frequência" sem trema e "/a".

export const OPCOES_FREQUENCIA = [
  { value: 0, label: 'Nenhuma vez' },
  { value: 1, label: 'Vários dias' },
  { value: 2, label: 'Mais da metade dos dias' },
  { value: 3, label: 'Quase todos os dias' },
] as const

export interface Instrumento {
  /** Chave do campo em `POST /api/avaliacoes` (Arquitetura, Quadro 6). */
  readonly id: 'phq9' | 'gad7'
  readonly title: string
  readonly stem: string
  readonly items: readonly string[]
}

export const PHQ9: Instrumento = {
  id: 'phq9',
  title: 'PHQ-9',
  stem: 'Durante as últimas 2 semanas, com que frequência você foi incomodado/a por qualquer um dos problemas abaixo?',
  items: [
    'Pouco interesse ou pouco prazer em fazer as coisas',
    'Se sentir “para baixo”, deprimido/a ou sem perspectiva',
    'Dificuldade para pegar no sono ou permanecer dormindo, ou dormir mais do que de costume',
    'Se sentir cansado/a ou com pouca energia',
    'Falta de apetite ou comendo demais',
    'Se sentir mal consigo mesmo/a — ou achar que você é um fracasso ou que decepcionou sua família ou você mesmo/a',
    'Dificuldade para se concentrar nas coisas, como ler o jornal ou ver televisão',
    'Lentidão para se movimentar ou falar, a ponto das outras pessoas perceberem? Ou o oposto – estar tão agitado/a ou irrequieto/a que você fica andando de um lado para o outro muito mais do que de costume',
    'Pensar em se ferir de alguma maneira ou que seria melhor estar morto/a',
  ],
}

export const GAD7: Instrumento = {
  id: 'gad7',
  title: 'GAD-7',
  stem: 'Durante as últimas 2 semanas, com que frequência você foi incomodado/a pelos problemas abaixo?',
  items: [
    'Sentir-se nervoso/a, ansioso/a ou muito tenso/a',
    'Não ser capaz de impedir ou de controlar as preocupações',
    'Preocupar-se muito com diversas coisas',
    'Dificuldade para relaxar',
    'Ficar tão agitado/a que se torna difícil permanecer sentado/a',
    'Ficar facilmente aborrecido/a ou irritado/a',
    'Sentir medo como se algo horrível fosse acontecer',
  ],
}

export const INSTRUMENTOS = [PHQ9, GAD7] as const

/** Posição do item 9 do PHQ-9 na lista `phq9` (regra R-A1). */
export const PHQ9_ITEM_RISCO = 8
