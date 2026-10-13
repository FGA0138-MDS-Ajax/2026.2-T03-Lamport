import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { authApi } from '../api/auth'
import { ApiError, describeError } from '../api/client'
import { Alert } from '../components/Alert'
import { TextField } from '../components/TextField'
import { PASSWORD_MIN_LENGTH, validateEmail, validateNewPassword } from '../validation'
import type { LoginLocationState } from './LoginPage'

interface FieldErrors {
  email?: string
  password?: string
  confirmPassword?: string
  acceptTerms?: string
}

export function RegisterPage() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [errors, setErrors] = useState<FieldErrors>({})
  const [submitError, setSubmitError] = useState<string>()
  const [submitting, setSubmitting] = useState(false)

  function validate(): FieldErrors {
    return {
      email: validateEmail(email),
      password: validateNewPassword(password),
      confirmPassword:
        confirmPassword === password ? undefined : 'As senhas informadas não coincidem.',
      acceptTerms: acceptTerms
        ? undefined
        : 'É necessário aceitar os termos de uso e a política de privacidade.',
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const fieldErrors = validate()
    setErrors(fieldErrors)
    setSubmitError(undefined)
    if (Object.values(fieldErrors).some(Boolean)) return

    setSubmitting(true)
    try {
      const user = await authApi.register({ email: email.trim(), password, accept_terms: true })
      navigate('/login', { state: { registeredEmail: user.email } satisfies LoginLocationState })
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setErrors({ email: 'Este e-mail já está cadastrado. Entre com sua conta.' })
      } else {
        setSubmitError(describeError(error))
      }
      setSubmitting(false)
    }
  }

  return (
    <section className="card auth-card" aria-labelledby="register-title">
      <h1 id="register-title">Criar conta</h1>
      <p className="muted">Seus registros ficam protegidos e visíveis apenas para você.</p>

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
          autoComplete="new-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          hint={`Use pelo menos ${PASSWORD_MIN_LENGTH} caracteres.`}
          error={errors.password}
        />
        <TextField
          label="Confirme a senha"
          type="password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          error={errors.confirmPassword}
        />

        <div className="field">
          <label className="checkbox">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(event) => setAcceptTerms(event.target.checked)}
              aria-invalid={errors.acceptTerms ? true : undefined}
              aria-describedby={errors.acceptTerms ? 'accept-terms-error' : undefined}
            />
            <span>
              Li e aceito os{' '}
              <Link to="/privacidade" target="_blank" rel="noreferrer">
                termos de uso e a política de privacidade
              </Link>
              .
            </span>
          </label>
          {errors.acceptTerms && (
            <p id="accept-terms-error" className="field-error">
              {errors.acceptTerms}
            </p>
          )}
        </div>

        <button type="submit" className="button button-primary" disabled={submitting}>
          {submitting ? 'Criando conta…' : 'Criar conta'}
        </button>
      </form>

      <p className="auth-switch">
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </section>
  )
}
