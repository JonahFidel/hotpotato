import { useEffect, useState } from 'react'
import type { GameState } from '../types'
import { Scoreboard } from '../components/Scoreboard'

type Props = {
  game: GameState
  passMessage: string | null
  busy: boolean
  onNext: () => void
  onFoul: () => void
  onTimeout: () => void
}

export function PlayScreen({ game, passMessage, busy, onNext, onFoul, onTimeout }: Props) {
  const [remaining, setRemaining] = useState(game.config.round_length_seconds)
  const holder = game.teams[game.holder_index]
  const nextTeam = game.teams[(game.holder_index + 1) % game.teams.length]
  const fraction = remaining / game.config.round_length_seconds

  useEffect(() => {
    if (!game.round_started_at) return
    let cancelled = false
    const started = new Date(game.round_started_at).getTime()
    const tick = () => {
      const left = Math.max(
        0,
        game.config.round_length_seconds - (Date.now() - started) / 1000,
      )
      setRemaining(left)
      if (left <= 0 && !cancelled) {
        cancelled = true
        onTimeout()
      }
    }
    tick()
    const id = window.setInterval(tick, 80)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [game.round_started_at, game.config.round_length_seconds, game.id, onTimeout])

  const seconds = Math.ceil(remaining)
  const urgent = remaining <= 10

  return (
    <section className={`panel play ${urgent ? 'urgent' : ''}`}>
      {passMessage && <div className="pass-banner">{passMessage}</div>}
      <p className="eyebrow">{holder.name} is holding it</p>
      <div className="timer" style={{ ['--heat' as string]: String(fraction) }}>
        {seconds}
      </div>
      <p className="phrase">{game.current_phrase}</p>
      <p className="hint">Get {holder.name} to say that. Then pass to {nextTeam.name}.</p>
      <div className="actions">
        <button className="primary" type="button" disabled={busy} onClick={onNext}>
          Guessed — next
        </button>
        <button className="danger" type="button" disabled={busy} onClick={onFoul}>
          Foul
        </button>
      </div>
      <Scoreboard game={game} compact />
    </section>
  )
}
