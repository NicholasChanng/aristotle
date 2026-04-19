from fastapi.testclient import TestClient
import os

from app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_world_returns_levels():
    client = TestClient(app)
    r = client.get("/api/v1/courses/cs188-sp2024/world")
    assert r.status_code == 200
    body = r.json()
    assert body["theme"] == "greek"
    assert len(body["levels"]) == 16  # 14 lectures + midterm + final


def test_generate_questions_returns_question_data():
    client = TestClient(app)
    r = client.post(
        "/api/v1/battles/generate-questions",
        json={"lecture_ids": ["03"], "num_of_questions": 3, "difficulty": 5},
    )
    has_keys = bool(os.getenv("ANTHROPIC_API_KEY")) and bool(os.getenv("OPENAI_API_KEY"))
    if has_keys:
        assert r.status_code == 200
        body = r.json()
        assert "question_data" in body
        assert body["num_of_questions"] == 3
        assert len(body["question_data"]) == 3
    else:
        assert r.status_code == 503
        assert "fallback is disabled" in r.json().get("detail", "").lower()
