const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST'
  body?: unknown
  token?: string | null
}

export async function request<T>(
  path: string,
  { method = 'GET', body, token }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let response: Response
  try {
    response = await fetch(`${API_URL}/api${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'Network error')
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    const detail = typeof data?.detail === 'string' ? data.detail : response.statusText
    throw new ApiError(response.status, detail)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export function describeError(error: unknown, byStatus: Record<number, string> = {}): string {
  if (!(error instanceof ApiError)) return 'Ocorreu um erro inesperado. Tente novamente.'
  if (byStatus[error.status]) return byStatus[error.status]
  if (error.status === 0) {
    return 'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.'
  }
  if (error.status === 422) return 'Verifique os dados informados e tente novamente.'
  if (error.status >= 500) {
    return 'O serviço está indisponível no momento. Tente novamente em instantes.'
  }
  return 'Ocorreu um erro inesperado. Tente novamente.'
}
