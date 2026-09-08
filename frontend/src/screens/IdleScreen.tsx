import type { CategorySummary, GameState } from '../types'
import { Scoreboard } from '../components/Scoreboard'

type Props = {
  game: GameState
  categories: CategorySummary[]
  busy: boolean
  onStart: () => void
  onPatch: (patch: { category_id?: string; round_length_seconds?: number; win_score?: number }) => void
  onNewGame: () => void
}

const LENGTH_PRESETS = [30, 45, 60, 90]

export function IdleScreen({ game, categories, busy, onStart, onPatch, onNewGame }: Props) {
  const holder = game.teams[game.holder_index]
  return (
    <section className="panel">
      <p className="eyebrow">Between rounds</p>
      <h1>Hand it to {holder.name}</h1>
      <p className="lede">
        First to {game.config.win_score}. Round is {game.config.round_length_seconds} seconds.
      </p>
      <Scoreboard game={game} />

      <label>
        Category
        <select
          value={game.config.category_id}
          disabled={busy}
          onChange={(event) => onPatch({ category_id: event.target.value })}
        >
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </label>

      <div className="presets">
        {LENGTH_PRESETS.map((seconds) => (
          <button
            type="button"
            key={seconds}
            disabled={busy}
            className={seconds === game.config.round_length_seconds ? 'chip on' : 'chip'}
            onClick={() => onPatch({ round_length_seconds: seconds })}
          >
            {seconds}s
          </button>
        ))}
      </div>

      <button className="primary" type="button" disabled={busy} onClick={onStart}>
        {busy ? 'Dealing…' : 'Start round'}
      </button>
      <button className="ghost" type="button" onClick={onNewGame}>
        New game
      </button>
    </section>
  )
}
