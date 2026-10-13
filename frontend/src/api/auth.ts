import { request } from './client'

export type Role = 'user' | 'curator' | 'admin'

export interface User {
  id: string
  email: string
  role: Role
  created_at: string
}

export interface RegisterData {
  email: string
  password: string
  accept_terms: boolean
}

interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export const authApi = {
  register: (data: RegisterData) => request<User>('/auth/register', { method: 'POST', body: data }),
  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', { method: 'POST', body: { email, password } }),
  logout: (token: string) => request<void>('/auth/logout', { method: 'POST', token }),
  me: (token: string) => request<User>('/users/me', { token }),
}
