import type { CategorySummary, CreateGameBody, GameState } from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    throw new Error(readDetail(body) || response.statusText)
  }
  return response.json() as Promise<T>
}

function readDetail(body: unknown): string {
  if (typeof body === 'object' && body && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
  }
  return ''
}

export const api = {
  categories: () => request<CategorySummary[]>('/api/categories'),
  createGame: (body: CreateGameBody) =>
    request<GameState>('/api/games', { method: 'POST', body: JSON.stringify(body) }),
  getGame: (id: string) => request<GameState>(`/api/games/${id}`),
  patchGame: (
    id: string,
    body: Partial<Pick<CreateGameBody, 'category_id' | 'round_length_seconds' | 'win_score'>>,
  ) => request<GameState>(`/api/games/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  startRound: (id: string) => request<GameState>(`/api/games/${id}/start-round`, { method: 'POST' }),
  next: (id: string) => request<GameState>(`/api/games/${id}/next`, { method: 'POST' }),
  timeout: (id: string) => request<GameState>(`/api/games/${id}/timeout`, { method: 'POST' }),
  foul: (id: string) => request<GameState>(`/api/games/${id}/foul`, { method: 'POST' }),
  bonus: (id: string, correct: boolean) =>
    request<GameState>(`/api/games/${id}/bonus`, {
      method: 'POST',
      body: JSON.stringify({ correct }),
    }),
}
