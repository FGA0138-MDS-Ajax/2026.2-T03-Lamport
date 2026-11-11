import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../auth/AuthContext'
import { BotaoAjuda } from './BotaoAjuda'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [leaving, setLeaving] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  async function handleLogout() {
    setMenuOpen(false)
    setLeaving(true)

    await logout()

    setLeaving(false)
    navigate('/login', { replace: true })
  }

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand" onClick={closeMenu}>
          Sintoniza
        </Link>

        <div className="header-actions">
          {/* Fora do bloco de sessão: o botão aparece com ou sem login (R11). */}
          <BotaoAjuda onClick={closeMenu} />

          {user && (
            <div className="header-session">
              <nav className="header-navigation" aria-label="Navegação principal">
                <NavLink to="/" end>
                  Início
                </NavLink>

                <NavLink to="/historico">Histórico</NavLink>
              </nav>

              <span className="header-email">{user.email}</span>

              <button
                type="button"
                className="button button-secondary desktop-logout"
                onClick={handleLogout}
                disabled={leaving}
              >
                {leaving ? 'Saindo…' : 'Sair'}
              </button>

              <button
                type="button"
                className="menu-toggle"
                aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
                aria-expanded={menuOpen}
                aria-controls="mobile-navigation"
                onClick={() => setMenuOpen((open) => !open)}
              >
                <span />
                <span />
                <span />
              </button>

              <nav
                id="mobile-navigation"
                className={`mobile-navigation ${menuOpen ? 'is-open' : ''}`}
                aria-label="Navegação móvel"
                aria-hidden={!menuOpen}
              >
                <NavLink to="/" end onClick={closeMenu}>
                  Início
                </NavLink>

                <NavLink to="/historico" onClick={closeMenu}>
                  Histórico
                </NavLink>

                <span className="mobile-menu-email">{user.email}</span>

                <button
                  type="button"
                  className="mobile-menu-logout"
                  onClick={handleLogout}
                  disabled={leaving}
                >
                  {leaving ? 'Saindo…' : 'Sair da conta'}
                </button>
              </nav>
            </div>
          )}
        </div>
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
