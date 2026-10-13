import { Navigate, Outlet, useLocation } from 'react-router'
import { LoadingState } from '../components/LoadingState'
import { useAuth } from './AuthContext'

export interface RedirectState {
  from?: string
}

export function RequireAuth() {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') return <LoadingState />
  if (status === 'anonymous') {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname } satisfies RedirectState} />
    )
  }
  return <Outlet />
}

export function GuestOnly() {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') return <LoadingState />
  if (status === 'authenticated') {
    const from = (location.state as RedirectState | null)?.from
    return <Navigate to={from ?? '/'} replace />
  }
  return <Outlet />
}
