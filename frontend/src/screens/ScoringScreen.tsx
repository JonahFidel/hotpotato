import type { GameState } from '../types'
import { Scoreboard } from '../components/Scoreboard'

type Props = {
  game: GameState
  busy: boolean
  onBonus: (correct: boolean) => void
}

export function ScoringScreen({ game, busy, onBonus }: Props) {
  const caught = game.caught_index != null ? game.teams[game.caught_index] : null
  const scorer = game.scoring_team_index != null ? game.teams[game.scoring_team_index] : null
  const reason = game.end_reason === 'foul' ? 'called a foul' : 'got caught holding it'

  return (
    <section className="panel scoring">
      <p className="eyebrow">{reason}</p>
      <h1>{caught?.name} was holding it</h1>
      <p className="lede">
        {scorer?.name} already has 1 point. Steal a bonus if they can guess the leftover phrase.
      </p>
      <p className="phrase leftover">{game.leftover_phrase}</p>
      <div className="actions">
        <button className="primary" type="button" disabled={busy} onClick={() => onBonus(true)}>
          {scorer?.name} stole it
        </button>
        <button className="ghost" type="button" disabled={busy} onClick={() => onBonus(false)}>
          No steal
        </button>
      </div>
      <Scoreboard game={game} />
    </section>
  )
}
