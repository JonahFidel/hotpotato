# Hotpotato

A pass-around party game in the spirit of Catchphrase: one phone, two or more teams, a ticking clock. Get your team to say the phrase, then hand the device to the **next** team. Don't be holding it when time runs out.

This is an unofficial original-phrase game. It does not use Hasbro's name, UI, or word lists.

## Why the code is shaped this way

| Layer | Lives in | Job |
|---|---|---|
| **Domain** | `backend/app/domain/` | Rules only. No HTTP, no database. Easy to test. |
| **API** | `backend/app/api/` | Thin FastAPI routes: parse request → call domain → save. |
| **Data** | `backend/app/data/categories/` | One JSON file per category pack. |
| **UI** | `frontend/` | Mobile-first React. Talks to the API; does not invent scoring rules. |

If you want a new house rule (different win score, longer rounds, more teams), start in `GameConfig` and `engine.py`, write a pytest, then expose it on the API. The UI should stay a client of that contract.

## Rules (including 3+ teams)

- Teams sit in a circle: Team 1 → Team 2 → … → Team N → Team 1.
- On a correct guess, pass to the next team and tap **Guessed — next**.
- On timeout or foul, the holding team is caught. The **next** team gets 1 point and may steal the leftover phrase for a bonus point.
- The caught team starts the following round (they still hold the phone).
- First team to the win score (default 7) wins.
- Clue with words or gestures. No rhymes, no first letter, no saying part of the phrase.

## Run it locally

You need two terminals.

Backend (from `backend/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to the FastAPI server.

API docs while the backend is running: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Run the rule tests:

```bash
cd backend
.venv/bin/pytest
```

## Hosted service

The public game is the Render web service in `render.yaml`.
That service builds `Dockerfile` and serves the React screen and `/api` on one origin.
Open that service URL to play.
The health check is `GET /api/health`.

## Add a category

1. Copy any file in `backend/app/data/categories/`.
2. Give it a unique `id`, a display `name`, and a `phrases` array (original phrases only).
3. Restart the backend (or let `--reload` pick it up). The new pack appears in the category dropdown automatically.

Example:

```json
{
  "id": "decades",
  "name": "Decades",
  "phrases": ["floppy disk", "pay phone", "walkman"]
}
```

Do not paste copyrighted official word lists into these files.
