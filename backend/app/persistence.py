from datetime import datetime, timezone

from sqlmodel import Field, Session, SQLModel, create_engine, select

from app.domain.models import GameState

DATABASE_URL = "sqlite:///./hotpotato.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class GameRow(SQLModel, table=True):
    id: str = Field(primary_key=True)
    state_json: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def configure_engine(url: str = DATABASE_URL) -> None:
    global engine
    engine = create_engine(url, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class GameStore:
    def save(self, session: Session, state: GameState) -> GameState:
        row = session.get(GameRow, state.id)
        payload = state.model_dump_json()
        now = datetime.now(timezone.utc)
        if row is None:
            session.add(GameRow(id=state.id, state_json=payload, updated_at=now))
        else:
            row.state_json = payload
            row.updated_at = now
            session.add(row)
        session.commit()
        return state

    def get(self, session: Session, game_id: str) -> GameState | None:
        row = session.get(GameRow, game_id)
        if row is None:
            return None
        return GameState.model_validate_json(row.state_json)

    def list_ids(self, session: Session) -> list[str]:
        rows = session.exec(select(GameRow.id)).all()
        return list(rows)
