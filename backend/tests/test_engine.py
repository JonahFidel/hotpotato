from collections.abc import Sequence

from app.domain.deck import pick_phrase
from app.domain.engine import (
    create_game,
    foul,
    next_phrase,
    resolve_bonus,
    start_round,
    timeout,
    update_config,
)
from app.domain.errors import IllegalTransition, InvalidConfig
from app.domain.models import GameConfig, GameState, Phase


def _config(**overrides) -> GameConfig:
    data = {
        "teams": ["Red", "Blue"],
        "category_id": "variety",
        "round_length_seconds": 60,
        "win_score": 7,
    }
    data.update(overrides)
    return GameConfig.model_validate(data)


def _game(**overrides) -> GameState:
    return create_game("game-1", _config(**overrides))


def test_create_game_starts_idle_with_zero_scores():
    state = _game(teams=["Alpha", "Bravo", "Charlie"])
    assert state.phase == Phase.IDLE
    assert [team.score for team in state.teams] == [0, 0, 0]
    assert state.holder_index == 0
    assert state.config.round_length_seconds == 60


def test_rejects_fewer_than_two_teams():
    try:
        _config(teams=["Only"])
        assert False, "expected validation error"
    except Exception:
        pass


def test_start_round_deals_phrase_and_starts_timer():
    state = start_round(_game(), "hot potato")
    assert state.phase == Phase.ROUND_ACTIVE
    assert state.current_phrase == "hot potato"
    assert state.round_started_at is not None
    assert "hot potato" in state.used_phrases


def test_next_phrase_rotates_holder_around_three_teams():
    state = start_round(_game(teams=["A", "B", "C"]), "one")
    state = next_phrase(state, "two")
    assert state.holder_index == 1
    state = next_phrase(state, "three")
    assert state.holder_index == 2
    state = next_phrase(state, "four")
    assert state.holder_index == 0
    assert state.current_phrase == "four"


def test_timeout_awards_point_to_next_team_not_holder():
    state = start_round(_game(teams=["A", "B", "C"]), "stuck phrase")
    state = next_phrase(state, "still stuck")
    assert state.holder_index == 1
    state = timeout(state)
    assert state.phase == Phase.SCORING
    assert state.caught_index == 1
    assert state.scoring_team_index == 2
    assert [team.score for team in state.teams] == [0, 0, 1]
    assert state.leftover_phrase == "still stuck"
    assert state.holder_index == 1


def test_foul_same_scoring_as_timeout():
    state = foul(start_round(_game(), "illegal clue"))
    assert state.end_reason.value == "foul"
    assert state.teams[1].score == 1
    assert state.teams[0].score == 0


def test_bonus_correct_adds_second_point():
    state = timeout(start_round(_game(), "leftover"))
    state = resolve_bonus(state, True)
    assert state.teams[1].score == 2
    assert state.phase == Phase.IDLE
    assert state.holder_index == 0


def test_bonus_miss_keeps_single_point_and_returns_idle():
    state = resolve_bonus(timeout(start_round(_game(), "leftover")), False)
    assert state.teams[1].score == 1
    assert state.phase == Phase.IDLE
    assert state.leftover_phrase is None


def test_first_team_to_win_score_wins_after_bonus():
    state = _game(win_score=2)
    state = timeout(start_round(state, "a"))
    state = resolve_bonus(state, True)
    assert state.phase == Phase.GAME_OVER
    assert state.winner_index == 1
    assert state.teams[1].score == 2


def test_cannot_change_category_during_round():
    state = start_round(_game(), "phrase")
    try:
        update_config(state, category_id="sports")
        assert False, "should not allow mid-round category change"
    except IllegalTransition:
        pass


def test_can_change_round_length_while_idle():
    state = update_config(_game(), round_length_seconds=90, category_id="sports")
    assert state.config.round_length_seconds == 90
    assert state.config.category_id == "sports"


def test_cannot_next_phrase_while_idle():
    try:
        next_phrase(_game(), "nope")
        assert False, "expected illegal transition"
    except IllegalTransition:
        pass


def test_pick_phrase_recycles_when_deck_exhausted():
    phrases: Sequence[str] = ["a", "b"]
    phrase, recycled = pick_phrase(phrases, ["a", "b"])
    assert recycled is True
    assert phrase in phrases


def test_invalid_round_length_rejected():
    try:
        _config(round_length_seconds=1)
        assert False, "expected invalid config"
    except Exception:
        pass


def test_caught_team_starts_the_next_round():
    state = start_round(_game(teams=["A", "B", "C"]), "one")
    state = next_phrase(state, "two")
    state = timeout(state)
    state = resolve_bonus(state, False)
    assert state.phase == Phase.IDLE
    assert state.holder_index == 1
    state = start_round(state, "three")
    assert state.holder_index == 1
