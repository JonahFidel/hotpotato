from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.api.schemas import BonusRequest, CreateGameRequest, PatchGameRequest
from app.catalog import CategoryPack, summaries
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
from app.domain.models import GameConfig, GameState
from app.persistence import GameStore, get_session

router = APIRouter()
store = GameStore()


def get_packs(request: Request) -> dict[str, CategoryPack]:
    return request.app.state.packs


@router.get("/categories")
def list_categories(packs: dict[str, CategoryPack] = Depends(get_packs)):
    return summaries(packs)


@router.post("/games", response_model=GameState)
def create(
    body: CreateGameRequest,
    session: Session = Depends(get_session),
    packs: dict[str, CategoryPack] = Depends(get_packs),
):
    _require_category(body.category_id, packs)
    try:
        state = create_game(
            str(uuid4()),
            GameConfig(
                teams=body.teams,
                category_id=body.category_id,
                round_length_seconds=body.round_length_seconds,
                win_score=body.win_score,
            ),
        )
    except InvalidConfig as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return store.save(session, state)


@router.get("/games/{game_id}", response_model=GameState)
def get_game(game_id: str, session: Session = Depends(get_session)):
    return _load(session, game_id)


@router.patch("/games/{game_id}", response_model=GameState)
def patch_game(
    game_id: str,
    body: PatchGameRequest,
    session: Session = Depends(get_session),
    packs: dict[str, CategoryPack] = Depends(get_packs),
):
    if body.category_id is not None:
        _require_category(body.category_id, packs)
    state = _load(session, game_id)
    try:
        state = update_config(
            state,
            category_id=body.category_id,
            round_length_seconds=body.round_length_seconds,
            win_score=body.win_score,
        )
    except (IllegalTransition, InvalidConfig) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return store.save(session, state)


@router.post("/games/{game_id}/start-round", response_model=GameState)
def start(
    game_id: str,
    session: Session = Depends(get_session),
    packs: dict[str, CategoryPack] = Depends(get_packs),
):
    state = _load(session, game_id)
    phrase, recycled = _deal(state, packs)
    if recycled:
        state = state.model_copy(update={"used_phrases": []})
    try:
        state = start_round(state, phrase)
    except (IllegalTransition, InvalidConfig) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return store.save(session, state)


@router.post("/games/{game_id}/next", response_model=GameState)
def guessed(
    game_id: str,
    session: Session = Depends(get_session),
    packs: dict[str, CategoryPack] = Depends(get_packs),
):
    state = _load(session, game_id)
    phrase, recycled = _deal(state, packs)
    if recycled:
        state = state.model_copy(update={"used_phrases": []})
    try:
        state = next_phrase(state, phrase)
    except (IllegalTransition, InvalidConfig) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return store.save(session, state)


@router.post("/games/{game_id}/timeout", response_model=GameState)
def buzz(game_id: str, session: Session = Depends(get_session)):
    return _end(session, game_id, timeout)


@router.post("/games/{game_id}/foul", response_model=GameState)
def call_foul(game_id: str, session: Session = Depends(get_session)):
    return _end(session, game_id, foul)


@router.post("/games/{game_id}/bonus", response_model=GameState)
def bonus(game_id: str, body: BonusRequest, session: Session = Depends(get_session)):
    state = _load(session, game_id)
    try:
        state = resolve_bonus(state, body.correct)
    except IllegalTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return store.save(session, state)


def _end(session: Session, game_id: str, action) -> GameState:
    state = _load(session, game_id)
    try:
        state = action(state)
    except IllegalTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return store.save(session, state)


def _deal(state: GameState, packs: dict[str, CategoryPack]) -> tuple[str, bool]:
    pack = _require_category(state.config.category_id, packs)
    return pick_phrase(pack.phrases, state.used_phrases)


def _load(session: Session, game_id: str) -> GameState:
    state = store.get(session, game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


def _require_category(category_id: str, packs: dict[str, CategoryPack]) -> CategoryPack:
    pack = packs.get(category_id)
    if pack is None:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category_id}")
    return pack
