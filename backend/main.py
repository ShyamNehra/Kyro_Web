"""
main.py — FastAPI WebSocket backend for Infinite Gomoku
Manages a game session per WebSocket connection.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio 
import random
import json

from model import GameModel
from ai import get_best_move

app = FastAPI(title="Gomoku WebSocket Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "message": message,
    }

@app.get("/")
async def health_check():
    return {"status": "I am awake!"}

@app.websocket("/ws/game")
async def game_endpoint(websocket: WebSocket):
    await websocket.accept()

    model = GameModel()
    AI_PLAYER = "O"
    HUMAN_PLAYER = "X"
    current_mode = "ai"  # Default mode

    await websocket.send_text(json.dumps(_build_state(model, "Connected. Choose a mode.")))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            action = data.get("action")

            # ── Start Game ─────────────────────────────────────────────────
            if action == "start":
                current_mode = data.get("mode", "ai")
                model.reset()
                msg = "Game started. Your turn (X)." if current_mode == "ai" else "PvP Started. X goes first."
                await websocket.send_text(json.dumps(_build_state(model, msg)))
                continue

            # ── Reset (Restart) ────────────────────────────────────────────
            if action == "reset":
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