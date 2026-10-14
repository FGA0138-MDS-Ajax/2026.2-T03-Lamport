import { useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router'
import { describeError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { Alert } from '../components/Alert'
import { TextField } from '../components/TextField'
import { validateEmail } from '../validation'

export interface LoginLocationState {
  registeredEmail?: string
}

interface FieldErrors {
  email?: string
  password?: string
}

export function LoginPage() {
  const { login } = useAuth()
  const registeredEmail = (useLocation().state as LoginLocationState | null)?.registeredEmail

  const [email, setEmail] = useState(registeredEmail ?? '')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<FieldErrors>({})
  const [submitError, setSubmitError] = useState<string>()
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const fieldErrors: FieldErrors = {
      email: validateEmail(email),
      password: password ? undefined : 'Informe sua senha.',
    }
    setErrors(fieldErrors)
    setSubmitError(undefined)
    if (fieldErrors.email || fieldErrors.password) return

    setSubmitting(true)
    try {
      // On success the GuestOnly guard redirects to the private area.
      await login(email.trim(), password)
    } catch (error) {
      setSubmitError(
        describeError(error, {
          401: 'E-mail ou senha incorretos.',
          429: 'Muitas tentativas sem sucesso. Aguarde alguns minutos e tente novamente.',
        }),
      )
      setSubmitting(false)
    }
  }

  return (
    <section className="card auth-card" aria-labelledby="login-title">
      <h1 id="login-title">Entrar</h1>
      <p className="muted">Acesse sua conta para acompanhar seu bem-estar.</p>

      {registeredEmail && !submitError && (
        <Alert tone="success">Conta criada com sucesso. Entre com seu e-mail e senha.</Alert>
      )}
      {submitError && <Alert tone="error">{submitError}</Alert>}

      <form onSubmit={handleSubmit} noValidate>
        <TextField
          label="E-mail"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          error={errors.email}
        />
        <TextField
          label="Senha"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={errors.password}
        />
        <button type="submit" className="button button-primary" disabled={submitting}>
          {submitting ? 'Entrando…' : 'Entrar'}
        </button>
      </form>

      <p className="auth-switch">
        Ainda não tem conta? <Link to="/cadastro">Criar conta</Link>
      </p>
    </section>
  )
}
