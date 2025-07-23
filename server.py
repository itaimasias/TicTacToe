import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import redis.asyncio as redis
from game import TicTacToe

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
GAME_CHANNEL = "tic-tac-toe-sync"

app = FastAPI()
games = {}
connections = {}

async def broadcast(game_id, msg):
    for ws in connections.get(game_id, []):
        try:
            await ws.send_text(json.dumps(msg))
        except:
            pass

async def redis_subscriber():
    r = redis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe(GAME_CHANNEL)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
        if message:
            data = json.loads(message["data"])
            game_id = data["game_id"]
            if game_id in games:
                games[game_id].board = data["board"]
                games[game_id].next_turn = data["nextTurn"]
                games[game_id].winner = data.get("winner")
                await broadcast(game_id, {
                    "type": "update",
                    "board": games[game_id].board,
                    "nextTurn": games[game_id].next_turn,
                    "winner": games[game_id].winner,
                })
        await asyncio.sleep(0.01)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_subscriber())

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await websocket.accept()
    if game_id not in games:
        games[game_id] = TicTacToe()
        connections[game_id] = []
    connections[game_id].append(websocket)
    r = redis.from_url(REDIS_URL)
    try:
        await websocket.send_text(json.dumps({
            "type": "update",
            "board": games[game_id].board,
            "nextTurn": games[game_id].next_turn,
            "winner": games[game_id].winner,
        }))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg["type"] == "move":
                row, col = int(msg["row"]), int(msg["col"])
                game = games[game_id]
                if not (0 <= row < 3 and 0 <= col < 3):
                    await websocket.send_text(json.dumps({"type": "error", "message": "Out of bounds"}))
                    continue
                valid = game.make_move(row, col, player_id)
                if not valid:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Invalid move"}))
                    continue

                await r.publish(GAME_CHANNEL, json.dumps({
                    "game_id": game_id,
                    "msg": msg,
                    "board": game.board,
                    "nextTurn": game.next_turn,
                    "winner": game.winner,
                }))
                await broadcast(game_id, {
                    "type": "update",
                    "board": game.board,
                    "nextTurn": game.next_turn,
                    "winner": game.winner,
                })

                if game.winner and game.winner != "draw":
                    await broadcast(game_id, {"type": "win", "winner": game.winner})
                elif game.winner == "draw":
                    await broadcast(game_id, {"type": "draw"})
    except WebSocketDisconnect:
        connections[game_id].remove(websocket)
    finally:
        await r.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")
