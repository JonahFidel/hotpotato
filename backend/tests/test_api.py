from fastapi.testclient import TestClient

from app.main import app
from app.persistence import configure_engine, init_db


def test_create_start_and_timeout(tmp_path):
    configure_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db()
    with TestClient(app) as client:
        categories = client.get("/api/categories")
        assert categories.status_code == 200
        assert any(item["id"] == "variety" for item in categories.json())

        created = client.post(
            "/api/games",
            json={
                "teams": ["Red", "Blue", "Green"],
                "category_id": "variety",
                "round_length_seconds": 45,
                "win_score": 7,
            },
        )
        assert created.status_code == 200
        game = created.json()
        assert game["config"]["round_length_seconds"] == 45
        assert len(game["teams"]) == 3

        started = client.post(f"/api/games/{game['id']}/start-round")
        assert started.status_code == 200
        assert started.json()["phase"] == "round_active"
        assert started.json()["current_phrase"]

        buzzed = client.post(f"/api/games/{game['id']}/timeout")
        assert buzzed.status_code == 200
        body = buzzed.json()
        assert body["phase"] == "scoring"
        assert body["teams"][1]["score"] == 1
        assert body["teams"][0]["score"] == 0
