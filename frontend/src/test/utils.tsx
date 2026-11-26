import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { vi } from 'vitest'
import { App } from '../App'
import { AuthProvider } from '../auth/AuthProvider'

interface MockResponse {
  status: number
  body?: unknown
}

// Uma lista de respostas é devolvida em sequência; a última se repete nas chamadas seguintes.
export function mockApi(routes: Record<string, MockResponse | MockResponse[]>) {
  const calls: Record<string, number> = {}
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const key = `${init?.method ?? 'GET'} ${new URL(String(input)).pathname}`
    const entry = routes[key]
    if (!entry) throw new Error(`Unexpected request: ${key}`)
    const index = calls[key] ?? 0
    calls[key] = index + 1
    const route = Array.isArray(entry) ? entry[Math.min(index, entry.length - 1)] : entry
    return new Response(route.body === undefined ? null : JSON.stringify(route.body), {
      status: route.status,
      headers: { 'Content-Type': 'application/json' },
    })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

export function renderApp(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  )
}

export const testUser = {
  id: '6f1c2a4e-0d7b-4b8e-9a43-2a1f6f0b9c11',
  email: 'ana@example.com',
  criado_em: '2026-10-13T12:00:00Z',
}
