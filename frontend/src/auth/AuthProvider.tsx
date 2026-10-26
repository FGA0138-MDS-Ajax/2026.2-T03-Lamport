import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { authApi, type User } from '../api/auth'
import { AuthContext, type AuthContextValue } from './AuthContext'

// sessionStorage keeps the session across reloads but drops it when the tab is closed,
// which suits the sensitive nature of the data and shared devices.
const TOKEN_KEY = 'sintoniza.token'

type Session =
  | { status: 'loading' }
  | { status: 'anonymous' }
  | { status: 'authenticated'; user: User; token: string }

function initialSession(): Session {
  return sessionStorage.getItem(TOKEN_KEY) ? { status: 'loading' } : { status: 'anonymous' }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session>(initialSession)

  useEffect(() => {
    const token = sessionStorage.getItem(TOKEN_KEY)
    if (!token) return

    let active = true
    authApi
      .me(token)
      .then((user) => {
        if (active) setSession({ status: 'authenticated', user, token })
      })
      .catch(() => {
        if (!active) return
        sessionStorage.removeItem(TOKEN_KEY)
        setSession({ status: 'anonymous' })
      })
    return () => {
      active = false
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token: token } = await authApi.login(email, password)
    const user = await authApi.me(token)
    sessionStorage.setItem(TOKEN_KEY, token)
    setSession({ status: 'authenticated', user, token })
  }, [])

  const logout = useCallback(async () => {
    if (session.status === 'authenticated') {
      try {
        await authApi.logout(session.token)
      } catch {
        // The local session is cleared anyway; the token expires on its own.
      }
    }
    sessionStorage.removeItem(TOKEN_KEY)
    setSession({ status: 'anonymous' })
  }, [session])

  const value = useMemo<AuthContextValue>(
    () => ({
      status: session.status,
      user: session.status === 'authenticated' ? session.user : null,
      token: session.status === 'authenticated' ? session.token : null,
      login,
      logout,
    }),
    [session, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
