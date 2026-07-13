from fastapi.testclient import TestClient

from app.main import APP_COMMIT, APP_VERSION, GameState, app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "version": APP_VERSION,
        "commit": APP_COMMIT,
    }


def test_frontend_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "Zgadnij liczbę" in response.text


def test_guess_too_low():
    GameState.secret_number = 50
    GameState.attempts = 0

    response = client.post("/guess", json={"number": 25})

    assert response.status_code == 200
    assert response.json()["result"] == "too_low"
    assert response.json()["attempts"] == 1


def test_guess_too_high():
    GameState.secret_number = 50
    GameState.attempts = 0

    response = client.post("/guess", json={"number": 75})

    assert response.status_code == 200
    assert response.json()["result"] == "too_high"
    assert response.json()["attempts"] == 1


def test_guess_correct_and_reset():
    GameState.secret_number = 50
    GameState.attempts = 0

    response = client.post("/guess", json={"number": 50})

    assert response.status_code == 200
    assert response.json()["result"] == "correct"
    assert response.json()["attempts"] == 1
    assert GameState.attempts == 0


def test_guess_validation_error():
    response = client.post("/guess", json={"number": 901})

    assert response.status_code == 422


def test_reset_game_by_header():
    GameState.secret_number = 50
    GameState.attempts = 5

    response = client.post("/guess", headers={"X-Reset-Game": "true"})

    assert response.status_code == 200
    assert response.json()["result"] == "reset"
    assert response.json()["attempts"] == 0
