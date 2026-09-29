from fastapi.testclient import TestClient

from app.main import app
from app.persistence import configure_engine, init_db


def test_same_origin_ui_and_api(tmp_path, monkeypatch):
    ui = tmp_path / "dist"
    ui.mkdir()
    (ui / "index.html").write_text(
        "<!doctype html><title>Hotpotato</title><h1>Play</h1>",
        encoding="utf-8",
    )
    (ui / "app.js").write_text("console.log('hotpotato')", encoding="utf-8")
    monkeypatch.setenv("STATIC_DIR", str(ui))
    configure_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db()

    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "text/html" in page.headers["content-type"]
        assert "Hotpotato" in page.text

        script = client.get("/app.js")
        assert script.status_code == 200
        assert "hotpotato" in script.text

        missing = client.get("/missing.js")
        assert missing.status_code == 404

        escaped = client.get("/..%2Fpyproject.toml")
        assert escaped.status_code == 404

        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["ok"] is True

        unknown_api = client.get("/api/does-not-exist")
        assert unknown_api.status_code == 404

        docs = client.get("/docs")
        assert docs.status_code == 200


def test_root_is_not_ui_without_a_build(tmp_path, monkeypatch):
    monkeypatch.setenv("STATIC_DIR", str(tmp_path / "missing"))
    configure_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db()

    with TestClient(app) as client:
        assert client.get("/").status_code == 404
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["ok"] is True
