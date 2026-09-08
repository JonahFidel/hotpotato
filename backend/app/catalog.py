from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

CATEGORIES_DIR = Path(__file__).resolve().parent / "data" / "categories"


class CategoryPack(BaseModel):
    id: str
    name: str
    phrases: list[str] = Field(min_length=1)


class CategorySummary(BaseModel):
    id: str
    name: str
    phrase_count: int


def load_packs(directory: Path = CATEGORIES_DIR) -> dict[str, CategoryPack]:
    packs: dict[str, CategoryPack] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        pack = CategoryPack.model_validate(payload)
        packs[pack.id] = pack
    if not packs:
        raise RuntimeError(f"No category packs found in {directory}")
    return packs


def summaries(packs: dict[str, CategoryPack]) -> list[CategorySummary]:
    return [
        CategorySummary(id=pack.id, name=pack.name, phrase_count=len(pack.phrases))
        for pack in packs.values()
    ]
