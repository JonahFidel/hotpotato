import type { GameState } from '../types'

export function Scoreboard({ game, compact = false }: { game: GameState; compact?: boolean }) {
  return (
    <ol className={`scores ${compact ? 'scores-compact' : ''}`}>
      {game.teams.map((team, index) => {
        const holding = game.holder_index === index && game.phase !== 'game_over'
        const winning = game.winner_index === index
        return (
          <li key={`${team.name}-${index}`} className={holding ? 'holding' : winning ? 'winner' : ''}>
            <span className="score-name">{team.name}</span>
            <span className="score-value">{team.score}</span>
          </li>
        )
      })}
    </ol>
  )
}
