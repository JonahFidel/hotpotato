export type Phase = 'idle' | 'round_active' | 'scoring' | 'game_over'
export type EndReason = 'timeout' | 'foul'

export type Team = {
  name: string
  score: number
}

export type GameConfig = {
  round_length_seconds: number
  win_score: number
  teams: string[]
  category_id: string
}

export type GameState = {
  id: string
  config: GameConfig
  teams: Team[]
  phase: Phase
  holder_index: number
  current_phrase: string | null
  used_phrases: string[]
  round_started_at: string | null
  caught_index: number | null
  scoring_team_index: number | null
  leftover_phrase: string | null
  end_reason: EndReason | null
  winner_index: number | null
}

export type CategorySummary = {
  id: string
  name: string
  phrase_count: number
}

export type CreateGameBody = {
  teams: string[]
  category_id: string
  round_length_seconds: number
  win_score: number
}
