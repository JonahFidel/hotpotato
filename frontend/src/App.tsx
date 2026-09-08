import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api/client'
import { IdleScreen } from './screens/IdleScreen'
import { PlayScreen } from './screens/PlayScreen'
import { ScoringScreen } from './screens/ScoringScreen'
import { SetupScreen } from './screens/SetupScreen'
import { WinnerScreen } from './screens/WinnerScreen'
import type { CategorySummary, CreateGameBody, GameState } from './types'

const STORAGE_KEY = 'hotpotato.gameId'

export default function App() {
  const [categories, setCategories] = useState<CategorySummary[]>([])
  const [game, setGame] = useState<GameState | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [passMessage, setPassMessage] = useState<string | null>(null)
  const timeoutLock = useRef(false)

  useEffect(() => {
    api
      .categories()
      .then(setCategories)
      .catch((err: Error) => setError(err.message))
  }, [])

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (!saved) return
    api
      .getGame(saved)
      .then(setGame)
      .catch(() => window.localStorage.removeItem(STORAGE_KEY))
  }, [])

  useEffect(() => {
    timeoutLock.current = false
  }, [game?.round_started_at, game?.id])

  const run = useCallback(async (action: () => Promise<GameState>) => {
    setBusy(true)
    setError(null)
    try {
      const next = await action()
      setGame(next)
      window.localStorage.setItem(STORAGE_KEY, next.id)
      return next
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      return null
    } finally {
      setBusy(false)
    }
  }, [])

  async function handleCreate(body: CreateGameBody) {
    await run(() => api.createGame(body))
  }

  async function handleNext() {
    if (!game) return
    const previousHolder = game.teams[game.holder_index].name
    const next = await run(() => api.next(game.id))
    if (next) {
      const incoming = next.teams[next.holder_index].name
      setPassMessage(`Pass it — ${previousHolder} guessed. ${incoming}'s turn.`)
      window.setTimeout(() => setPassMessage(null), 1800)
    }
  }

  const handleTimeout = useCallback(() => {
    if (!game || timeoutLock.current) return
    timeoutLock.current = true
    void run(() => api.timeout(game.id)).then((next) => {
      if (!next) timeoutLock.current = false
    })
  }, [game, run])

  function newGame() {
    window.localStorage.removeItem(STORAGE_KEY)
    setGame(null)
    setError(null)
    setPassMessage(null)
  }

  return (
    <main className="shell">
      {error && <p className="error">{error}</p>}
      {!game && categories.length === 0 && !error && <p className="loading">Loading categories…</p>}
      {!game && categories.length > 0 && (
        <SetupScreen categories={categories} busy={busy} onCreate={handleCreate} />
      )}
      {game?.phase === 'idle' && (
        <IdleScreen
          game={game}
          categories={categories}
          busy={busy}
          onStart={() => run(() => api.startRound(game.id))}
          onPatch={(patch) => run(() => api.patchGame(game.id, patch))}
          onNewGame={newGame}
        />
      )}
      {game?.phase === 'round_active' && (
        <PlayScreen
          game={game}
          passMessage={passMessage}
          busy={busy}
          onNext={handleNext}
          onFoul={() => run(() => api.foul(game.id))}
          onTimeout={handleTimeout}
        />
      )}
      {game?.phase === 'scoring' && (
        <ScoringScreen game={game} busy={busy} onBonus={(correct) => run(() => api.bonus(game.id, correct))} />
      )}
      {game?.phase === 'game_over' && <WinnerScreen game={game} onNewGame={newGame} />}
    </main>
  )
}
