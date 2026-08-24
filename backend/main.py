"""
main.py — FastAPI WebSocket backend for Infinite Kyro
Manages a game session per WebSocket connection.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio 
import random
import json
import os

from model import GameModel
from ai import get_best_move

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Kyro WebSocket Server")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS via ALLOWED_ORIGINS env variable (comma-separated), falling back to "*"
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _serialize_board(board: dict) -> dict:
    return {f"{x},{y}": player for (x, y), player in board.items()}

def _build_state(model: GameModel, message: str = "") -> dict:
    return {
        "board": _serialize_board(model.board),
        "current_turn": model.current,
        "game_over": model.game_over,
        "winner": model.winner,
        "winning_line": model.winning_line,
        "message": message,
    }

@app.api_route("/", methods=["GET", "HEAD"])
@limiter.limit("30/minute")
async def root(request: Request):
    return {"status": "I am awake!"}

@app.websocket("/ws/game")
async def game_endpoint(websocket: WebSocket):
    await websocket.accept()

    model = GameModel()
    AI_PLAYER = "O"
    HUMAN_PLAYER = "X"
    current_mode = "ai"  # Default mode

    # Initial state is only sent upon request (sync_mode or reset)
    try:
        while True:
            raw = await websocket.receive_text()
            # Security: Limit incoming payload size (max 2048 bytes) to prevent memory exhaustion
            if len(raw) > 2048:
                await websocket.send_text(json.dumps({"error": "Payload size exceeds limit."}))
                continue

            try:
                data = json.loads(raw)
            except Exception:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format."}))
                continue

            if not isinstance(data, dict):
                await websocket.send_text(json.dumps({"error": "Invalid request object."}))
                continue

            action = data.get("action")

            # ── Sync Mode ──────────────────────────────────────────────────
            if action == "sync_mode":
                mode_input = data.get("mode")
                if mode_input in ("ai", "pvp"):
                    current_mode = mode_input
                msg = f"Mode synced to {current_mode}."
                await websocket.send_text(json.dumps(_build_state(model, msg)))
                continue

            # ── Reset (Restart) ────────────────────────────────────────────
            if action == "reset":
                mode_input = data.get("mode")
                if mode_input in ("ai", "pvp"):
                    current_mode = mode_input
                model.reset()
                msg = "Board reset. Your turn (X)." if current_mode == "ai" else "Board reset. X goes first."
                await websocket.send_text(json.dumps(_build_state(model, msg)))
                continue

            # ── Place Piece ────────────────────────────────────────────────
            if action == "place":
                if model.game_over:
                    continue

                try:
                    x, y = int(data["x"]), int(data["y"])
                    # Coordinate bounds check to prevent extreme values
                    if abs(x) > 100000 or abs(y) > 100000:
                        continue
                except (KeyError, ValueError, TypeError):
                    continue

                # --- AI MODE LOGIC ---
                if current_mode == "ai":
                    if model.current != HUMAN_PLAYER:
                        continue
                    if not model.place_piece(x, y):
                        continue
                    if model.game_over:
                        await websocket.send_text(json.dumps(_build_state(model, "You win! 🎉")))
                        continue
                    
                    # AI Turn
                    await websocket.send_text(json.dumps(_build_state(model, "AI is thinking…")))

                    await asyncio.sleep(random.uniform(1.0, 1.5))

                    ai_x, ai_y = get_best_move(model.board, AI_PLAYER)
                    model.place_piece(ai_x, ai_y)
                    
                    msg = f"AI plays ({ai_x},{ai_y}). AI wins! 🤖" if model.game_over else f"AI plays ({ai_x},{ai_y}). Your turn (X)."
                    await websocket.send_text(json.dumps(_build_state(model, msg)))

                # --- PVP MODE LOGIC ---
                elif current_mode == "pvp":
                    player_who_moved = model.current
                    if not model.place_piece(x, y):
                        continue
                    
                    if model.game_over:
                        msg = f"Player {player_who_moved} wins! 🎉"
                    else:
                        msg = f"Player {model.current}'s turn."
                        
                    await websocket.send_text(json.dumps(_build_state(model, msg)))

    except WebSocketDisconnect:
        pass
    except Exception:
        # Catch unexpected errors to prevent unhandled stack trace leakage
        pass


@app.api_route("/health", methods=["GET", "HEAD"])
@limiter.exempt
def health_check():
    return {"status": "ok"}