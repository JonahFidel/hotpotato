from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Phase(str, Enum):
    IDLE = "idle"
    ROUND_ACTIVE = "round_active"
    SCORING = "scoring"
    GAME_OVER = "game_over"


class EndReason(str, Enum):
    TIMEOUT = "timeout"
    FOUL = "foul"


class Team(BaseModel):
    name: str
    score: int = 0


class GameConfig(BaseModel):
    """Rules that can change without rewriting the engine.

    Add a field here (and handle it in engine.py) when you introduce a house rule.
    """

    round_length_seconds: int = Field(default=60, ge=10, le=300)
    win_score: int = Field(default=7, ge=1, le=99)
    teams: list[str]
    category_id: str

    @field_validator("teams")
    @classmethod
    def validate_teams(cls, teams: list[str]) -> list[str]:
        cleaned = [name.strip() for name in teams]
        if any(not name for name in cleaned):
            raise ValueError("Team names cannot be empty")
        if len(cleaned) < 2:
            raise ValueError("Need at least two teams")
        if len(set(name.lower() for name in cleaned)) != len(cleaned):
            raise ValueError("Team names must be unique")
        return cleaned

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, category_id: str) -> str:
        value = category_id.strip()
        if not value:
            raise ValueError("category_id is required")
        return value


class GameState(BaseModel):
    id: str
    config: GameConfig
    teams: list[Team]
    phase: Phase = Phase.IDLE
    holder_index: int = 0
    current_phrase: str | None = None
    used_phrases: list[str] = Field(default_factory=list)
    round_started_at: datetime | None = None
    caught_index: int | None = None
    scoring_team_index: int | None = None
    leftover_phrase: str | None = None
    end_reason: EndReason | None = None
    winner_index: int | None = None

    @property
    def team_count(self) -> int:
        return len(self.teams)

    def next_index(self, index: int | None = None) -> int:
        current = self.holder_index if index is None else index
        return (current + 1) % self.team_count
