import { useEffect, useId, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { describeError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { Alert } from './Alert'

/**
 * Exclusão da própria conta (Visão, R04; perfil P02). Pede confirmação antes de chamar
 * DELETE /api/me; depois encerra a sessão no navegador e volta à página inicial.
 */
export function ExcluirConta() {
  const { deleteAccount } = useAuth()
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string>()

  const titleId = useId()
  const descriptionId = useId()
  const openButtonRef = useRef<HTMLButtonElement>(null)
  const cancelButtonRef = useRef<HTMLButtonElement>(null)
  const wasConfirming = useRef(false)

  // Foco na opção segura ao abrir a confirmação; ao cancelar, volta para o botão que a abriu.
  useEffect(() => {
    if (confirming) cancelButtonRef.current?.focus()
    else if (wasConfirming.current) openButtonRef.current?.focus()
    wasConfirming.current = confirming
  }, [confirming])

  function handleCancel() {
    setConfirming(false)
    setError(undefined)
  }

  async function handleConfirm() {
    setDeleting(true)
    setError(undefined)
    try {
      await deleteAccount()
      navigate('/', { replace: true })
    } catch (err) {
      setError(
        describeError(err, {
          401: 'Sua sessão expirou. Entre novamente para excluir a conta.',
        }),
      )
      setDeleting(false)
    }
  }

  if (!confirming) {
    return (
      <div className="account-delete">
        <button
          ref={openButtonRef}
          type="button"
          className="button button-danger-outline"
          onClick={() => setConfirming(true)}
        >
          Excluir conta
        </button>
      </div>
    )
  }

  return (
    <div
      className="account-delete account-delete-confirm"
      role="alertdialog"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <h2 id={titleId}>Excluir sua conta?</h2>
      <p id={descriptionId}>
        Todos os seus dados (check-ins, avaliações e recomendações) serão apagados sem possibilidade
        de recuperação.
      </p>

      {error && <Alert tone="error">{error}</Alert>}

      <div className="account-delete-actions">
        <button
          ref={cancelButtonRef}
          type="button"
          className="button button-secondary"
          onClick={handleCancel}
          disabled={deleting}
        >
          Cancelar
        </button>
        <button
          type="button"
          className="button button-danger"
          onClick={handleConfirm}
          disabled={deleting}
        >
          {deleting ? 'Excluindo…' : 'Excluir definitivamente'}
        </button>
      </div>
    </div>
  )
}
