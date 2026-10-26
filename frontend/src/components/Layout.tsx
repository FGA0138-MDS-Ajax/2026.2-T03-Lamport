import { useState } from 'react'
import { Link, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../auth/AuthContext'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [leaving, setLeaving] = useState(false)

  async function handleLogout() {
    setLeaving(true)
    await logout()
    setLeaving(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Sintoniza
        </Link>
        {user && (
          <div className="header-session">
            <span className="header-email">{user.email}</span>
            <button
              type="button"
              className="button button-secondary"
              onClick={handleLogout}
              disabled={leaving}
            >
              {leaving ? 'Saindo…' : 'Sair'}
            </button>
          </div>
        )}
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <Link to="/privacidade">Termos de uso e privacidade</Link>
      </footer>
    </div>
  )
}
