import { Link } from 'react-router'
import { AJUDA_PATH } from '../constants/ajuda'

interface BotaoAjudaProps {
  onClick?: () => void
}

/** Botão "Preciso de ajuda agora" (R11): visível em todas as páginas, com ou sem login. */
export function BotaoAjuda({ onClick }: BotaoAjudaProps) {
  return (
    <Link to={AJUDA_PATH} className="button-help" onClick={onClick}>
      <span aria-hidden="true">♥</span>
      Preciso de ajuda agora
    </Link>
  )
}
