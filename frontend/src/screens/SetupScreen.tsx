import { useEffect, useState } from 'react'
import type { CategorySummary, CreateGameBody } from '../types'

const LENGTH_PRESETS = [30, 45, 60, 90]

type Props = {
  categories: CategorySummary[]
  busy: boolean
  onCreate: (body: CreateGameBody) => void
}

export function SetupScreen({ categories, busy, onCreate }: Props) {
  const [teams, setTeams] = useState(['Team 1', 'Team 2'])
  const [roundLength, setRoundLength] = useState(60)
  const [winScore, setWinScore] = useState(7)
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? '')

  useEffect(() => {
    if (!categoryId && categories[0]) {
      setCategoryId(categories[0].id)
    }
  }, [categories, categoryId])

  function updateTeam(index: number, name: string) {
    setTeams((current) => current.map((team, i) => (i === index ? name : team)))
  }

  return (
    <form
      className="panel setup"
      onSubmit={(event) => {
        event.preventDefault()
        onCreate({
          teams: teams.map((name) => name.trim()).filter(Boolean),
          category_id: categoryId,
          round_length_seconds: roundLength,
          win_score: winScore,
        })
      }}
    >
      <p className="eyebrow">Pass-around party game</p>
      <h1>Hotpotato</h1>
      <p className="lede">
        Get your team to say the phrase. Then toss the phone to the next team. Don&apos;t be holding it
        when the buzzer hits.
      </p>

      <fieldset>
        <legend>Teams</legend>
        {teams.map((team, index) => (
          <div className="row" key={index}>
            <input
              aria-label={`Team ${index + 1} name`}
              value={team}
              onChange={(event) => updateTeam(index, event.target.value)}
              maxLength={24}
              required
            />
            {teams.length > 2 && (
              <button
                type="button"
                className="ghost"
                onClick={() => setTeams((current) => current.filter((_, i) => i !== index))}
              >
                Remove
              </button>
            )}
          </div>
        ))}
        {teams.length < 8 && (
          <button
            type="button"
            className="ghost"
            onClick={() => setTeams((current) => [...current, `Team ${current.length + 1}`])}
          >
            Add a team
          </button>
        )}
      </fieldset>

      <fieldset>
        <legend>Round length</legend>
        <div className="presets">
          {LENGTH_PRESETS.map((seconds) => (
            <button
              type="button"
              key={seconds}
              className={seconds === roundLength ? 'chip on' : 'chip'}
              onClick={() => setRoundLength(seconds)}
            >
              {seconds}s
            </button>
          ))}
        </div>
        <label className="slider">
          <span>{roundLength} seconds</span>
          <input
            type="range"
            min={10}
            max={180}
            step={5}
            value={roundLength}
            onChange={(event) => setRoundLength(Number(event.target.value))}
          />
        </label>
      </fieldset>

      <label>
        First to
        <input
          type="number"
          min={1}
          max={99}
          value={winScore}
          onChange={(event) => setWinScore(Number(event.target.value))}
        />
        points
      </label>

      <label>
        Category
        <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} required>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name} ({category.phrase_count})
            </option>
          ))}
        </select>
      </label>

      <ul className="rules">
        <li>Clue with words or gestures.</li>
        <li>No rhymes, no first letter, no saying part of the phrase.</li>
        <li>Pass to the next team the instant they guess it.</li>
      </ul>

      <button className="primary" type="submit" disabled={busy || !categoryId}>
        {busy ? 'Starting…' : 'Start game'}
      </button>
    </form>
  )
}
