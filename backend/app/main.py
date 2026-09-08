from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
