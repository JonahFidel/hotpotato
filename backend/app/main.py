import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import router
from app.catalog import load_packs
from app.persistence import init_db

category_packs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    packs = load_packs()
    category_packs.clear()
    category_packs.update(packs)
    app.state.packs = packs
    yield


app = FastAPI(title="Hotpotato", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


@app.get("/api/health")
def health():
    return {"ok": True, "categories": len(category_packs)}


def resolve_static_dir() -> Path | None:
    """Directory of the built React app, when this process should serve it.

    Render sets STATIC_DIR in the image. Locally, a production-style build
    at frontend/dist is used when that folder exists.
    """
    raw = os.environ.get("STATIC_DIR")
    if raw is not None:
        path = Path(raw)
    else:
        path = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if not path.is_dir() or not (path / "index.html").is_file():
        return None
    return path.resolve()


def _frontend_file(full_path: str) -> Path:
    root = resolve_static_dir()
    if root is None or full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    relative = Path(full_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise HTTPException(status_code=404, detail="Not Found")
    if full_path in ("", "."):
        return root / "index.html"
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not Found") from None
    if candidate.is_file():
        return candidate
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/", include_in_schema=False)
def frontend_index() -> FileResponse:
    return FileResponse(_frontend_file(""))


@app.get("/{full_path:path}", include_in_schema=False)
def frontend_asset(full_path: str) -> FileResponse:
    return FileResponse(_frontend_file(full_path))
