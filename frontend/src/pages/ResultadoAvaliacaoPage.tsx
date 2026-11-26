import { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router'
import { useAuth } from '../auth/AuthContext'
import { avaliacoesApi, type ResultadoAvaliacao as ResultadoAvaliacaoType } from '../api/avaliacoes'
import { ResultadoAvaliacao } from '../components/ResultadoAvaliacao'
import { Alert } from '../components/Alert'
import { ApiError } from '../api/client'

interface LocationState {
  resultado?: ResultadoAvaliacaoType
}

type LoadState =
  | {
      id: string
      status: 'success'
      avaliacao: ResultadoAvaliacaoType
    }
  | { id: string; status: 'not-found' }
  | { id: string; status: 'error' }
  | null

export function ResultadoAvaliacaoPage() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const { token } = useAuth()

  const state = location.state as LocationState | null

  const [loadState, setLoadState] = useState<LoadState>(null)

  useEffect(() => {
    if (!id) return

    const avaliacaoId = id
    let cancelled = false

    async function loadAvaliacao() {
      try {
        if (!token) {
          throw new Error('Usuário não autenticado.')
        }

        const avaliacao = await avaliacoesApi.getAvaliacao(token, avaliacaoId)

        if (!cancelled) {
          setLoadState({
            id: avaliacaoId,
            status: 'success',
            avaliacao,
          })
        }
      } catch (error) {
        if (cancelled) return

        // 404: não existe ou pertence a outro usuário; 422: id que não é um UUID válido.
        if (error instanceof ApiError && (error.status === 404 || error.status === 422)) {
          setLoadState({
            id: avaliacaoId,
            status: 'not-found',
          })
          return
        }

        setLoadState({
          id: avaliacaoId,
          status: 'error',
        })
      }
    }

    void loadAvaliacao()

    return () => {
      cancelled = true
    }
  }, [id, token])

  // Resultado recém-criado, recebido pela navegação.
  if (!id && state?.resultado) {
    return <ResultadoAvaliacao resultado={state.resultado} recemRegistrada />
  }

  // Nenhum ID nem resultado recebido.
  if (!id) {
    return (
      <Alert tone="error">
        Nenhum resultado de avaliação foi encontrado. Acesse a avaliação novamente para visualizar
        seu resultado.
      </Alert>
    )
  }

  // A consulta ainda está em andamento ou o ID mudou.
  if (!loadState || loadState.id !== id) {
    return <p role="status">Carregando avaliação...</p>
  }

  if (loadState.status === 'not-found') {
    return (
      <Alert tone="error">
        Avaliação não encontrada. Verifique o endereço ou volte ao histórico.
      </Alert>
    )
  }

  if (loadState.status === 'error') {
    return (
      <Alert tone="error">Não foi possível carregar a avaliação. Tente novamente mais tarde.</Alert>
    )
  }

  return <ResultadoAvaliacao resultado={loadState.avaliacao} />
}
