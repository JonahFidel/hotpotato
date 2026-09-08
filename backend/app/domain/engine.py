from datetime import datetime, timezone

from app.domain.errors import IllegalTransition, InvalidConfig
from app.domain.models import EndReason, GameConfig, GameState, Phase, Team


def create_game(game_id: str, config: GameConfig) -> GameState:
    try:
        validated = GameConfig.model_validate(config.model_dump())
    except Exception as exc:
        raise InvalidConfig(str(exc)) from exc
    teams = [Team(name=name) for name in validated.teams]
    return GameState(id=game_id, config=validated, teams=teams)


def update_config(
    state: GameState,
    *,
    category_id: str | None = None,
    round_length_seconds: int | None = None,
    win_score: int | None = None,
) -> GameState:
    if state.phase != Phase.IDLE:
        raise IllegalTransition("Settings can only change when the timer is not running")
    data = state.config.model_dump()
    if category_id is not None:
        data["category_id"] = category_id
    if round_length_seconds is not None:
        data["round_length_seconds"] = round_length_seconds
    if win_score is not None:
        data["win_score"] = win_score
    try:
        config = GameConfig.model_validate(data)
    except Exception as exc:
        raise InvalidConfig(str(exc)) from exc
    return state.model_copy(update={"config": config})


def start_round(state: GameState, phrase: str) -> GameState:
    _require_phase(state, Phase.IDLE)
    if not phrase.strip():
        raise InvalidConfig("A round needs a phrase")
    used = [*state.used_phrases, phrase]
    return state.model_copy(
        update={
            "phase": Phase.ROUND_ACTIVE,
            "current_phrase": phrase,
            "used_phrases": used,
            "round_started_at": datetime.now(timezone.utc),
            "caught_index": None,
            "scoring_team_index": None,
            "leftover_phrase": None,
            "end_reason": None,
        }
    )


def next_phrase(state: GameState, phrase: str) -> GameState:
    """The current team guessed; pass the device to the next team."""
    _require_phase(state, Phase.ROUND_ACTIVE)
    if not phrase.strip():
        raise InvalidConfig("Need a new phrase after a guess")
    used = [*state.used_phrases, phrase]
    return state.model_copy(
        update={
            "holder_index": state.next_index(),
            "current_phrase": phrase,
            "used_phrases": used,
        }
    )


def timeout(state: GameState) -> GameState:
    return _end_round(state, EndReason.TIMEOUT)


def foul(state: GameState) -> GameState:
    return _end_round(state, EndReason.FOUL)


def resolve_bonus(state: GameState, correct: bool) -> GameState:
    """Award a steal point if the next team guessed the leftover phrase, then close the round."""
    _require_phase(state, Phase.SCORING)
    if state.scoring_team_index is None:
        raise IllegalTransition("Scoring team is missing")
    teams = [team.model_copy() for team in state.teams]
    if correct:
        teams[state.scoring_team_index].score += 1
    winner_index = _winner_index(teams, state.config.win_score)
    if winner_index is not None:
        return state.model_copy(
            update={
                "teams": teams,
                "phase": Phase.GAME_OVER,
                "winner_index": winner_index,
                "leftover_phrase": None,
                "current_phrase": None,
            }
        )
    return state.model_copy(
        update={
            "teams": teams,
            "phase": Phase.IDLE,
            "leftover_phrase": None,
            "current_phrase": None,
            "caught_index": None,
            "scoring_team_index": None,
            "end_reason": None,
        }
    )


def _end_round(state: GameState, reason: EndReason) -> GameState:
    _require_phase(state, Phase.ROUND_ACTIVE)
    caught = state.holder_index
    scorer = state.next_index(caught)
    teams = [team.model_copy() for team in state.teams]
    teams[scorer].score += 1
    return state.model_copy(
        update={
            "teams": teams,
            "phase": Phase.SCORING,
            "caught_index": caught,
            "scoring_team_index": scorer,
            "leftover_phrase": state.current_phrase,
            "current_phrase": None,
            "round_started_at": None,
            "end_reason": reason,
        }
    )


def _winner_index(teams: list[Team], win_score: int) -> int | None:
    for index, team in enumerate(teams):
        if team.score >= win_score:
            return index
    return None


def _require_phase(state: GameState, phase: Phase) -> None:
    if state.phase != phase:
        raise IllegalTransition(f"Need phase {phase.value}, currently {state.phase.value}")
