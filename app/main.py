import os
from datetime import datetime, timezone
from random import randint

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_COMMIT = os.getenv("APP_COMMIT", "local")


app = FastAPI(
    title="Number Guess API",
    description="API do zgadywania losowej liczby",
    version=APP_VERSION,
)


class GameState:
    secret_number: int = randint(1, 100)
    attempts: int = 0


class GuessRequest(BaseModel):
    number: int = Field(..., ge=1, le=100)


def reset_game() -> None:
    GameState.secret_number = randint(1, 100)
    GameState.attempts = 0


@app.get("/", response_class=HTMLResponse)
def frontend():
    return """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Number Guess API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #111827;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }

            .box {
                background: #1f2937;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                width: 360px;
            }

            input {
                padding: 10px;
                width: 100px;
                font-size: 18px;
                text-align: center;
            }

            button {
                padding: 10px 15px;
                margin: 5px;
                cursor: pointer;
            }

            #result {
                margin-top: 20px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Zgadnij liczbę</h1>
            <p>Podaj liczbę od 1 do 100</p>

            <input id="number" type="number" min="1" max="100" />
            <br><br>

            <button onclick="guessNumber()">Sprawdź liczbę</button>
            <button onclick="resetGame()">Reset</button>

            <div id="result"></div>
        </div>

        <script>
            async function guessNumber() {
                const numberInput = document.getElementById("number").value;
                const number = Number(numberInput);

                if (!numberInput || number < 1 || number > 100) {
                    document.getElementById("result").innerText =
                        "Podaj liczbę od 1 do 100.";
                    return;
                }

                const response = await fetch("/guess", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        number: number
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    document.getElementById("result").innerText =
                        "Podaj liczbę od 1 do 100.";
                    return;
                }

                document.getElementById("result").innerText =
                    data.message + " Próby: " + data.attempts;
            }

            async function resetGame() {
                const response = await fetch("/guess", {
                    method: "POST",
                    headers: {
                        "X-Reset-Game": "true"
                    }
                });

                const data = await response.json();

                if (!response.ok) {
                    document.getElementById("result").innerText =
                        "Nie udało się zresetować gry.";
                    return;
                }

                document.getElementById("result").innerText = data.message;
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version")
def version():
    return {
        "version": APP_VERSION,
        "commit": APP_COMMIT,
    }


@app.post("/guess")
def guess(
    payload: GuessRequest | None = None,
    x_reset_game: bool = Header(default=False),
):
    if x_reset_game:
        reset_game()
        return {
            "result": "reset",
            "message": "Gra została zresetowana. Wylosowano nową liczbę.",
            "attempts": GameState.attempts,
        }

    if payload is None:
        raise HTTPException(
            status_code=400,
            detail="Podaj liczbę w JSON, np. {'number': 50}",
        )

    GameState.attempts += 1

    if payload.number == GameState.secret_number:
        attempts = GameState.attempts
        reset_game()

        return {
            "result": "correct",
            "message": "Brawo, zgadłeś liczbę. Wylosowano nową liczbę.",
            "attempts": attempts,
        }

    if payload.number < GameState.secret_number:
        return {
            "result": "too_low",
            "message": "Za mało.",
            "attempts": GameState.attempts,
        }

    return {
        "result": "too_high",
        "message": "Za dużo.",
        "attempts": GameState.attempts,
    }