import { request } from './client'

export interface User {
  id: string
  email: string
  criado_em: string
}

export interface RegisterData {
  email: string
  senha: string
  aceite_termos: boolean
  maior_de_idade: boolean
}

export interface Terms {
  version: string
}

interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export const authApi = {
  register: (data: RegisterData) => request<User>('/auth/cadastro', { method: 'POST', body: data }),
  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', { method: 'POST', body: { email, senha: password } }),
  logout: (token: string) => request<void>('/auth/logout', { method: 'POST', token }),
  me: (token: string) => request<User>('/me', { token }),
}

export const termsApi = {
  get: () => request<Terms>('/terms'),
}
