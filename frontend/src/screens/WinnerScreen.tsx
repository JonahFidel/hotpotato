import type { GameState } from '../types'
import { Scoreboard } from '../components/Scoreboard'

type Props = {
  game: GameState
  onNewGame: () => void
}

export function WinnerScreen({ game, onNewGame }: Props) {
  const winner = game.winner_index != null ? game.teams[game.winner_index] : null
  return (
    <section className="panel winner">
      <p className="eyebrow">Game over</p>
      <h1>{winner?.name} wins</h1>
      <p className="lede">First to {game.config.win_score}. Everyone else was holding the potato.</p>
      <Scoreboard game={game} />
      <button className="primary" type="button" onClick={onNewGame}>
        Play again
      </button>
    </section>
  )
}
