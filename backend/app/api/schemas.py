from pydantic import BaseModel, Field

from app.domain.models import GameState


class CreateGameRequest(BaseModel):
    teams: list[str] = Field(min_length=2)
    category_id: str
    round_length_seconds: int = 60
    win_score: int = 7


class PatchGameRequest(BaseModel):
    category_id: str | None = None
    round_length_seconds: int | None = None
    win_score: int | None = None


class BonusRequest(BaseModel):
    correct: bool


class GameResponse(GameState):
    """API returns the domain GameState as-is so the UI stays in sync with tests."""
