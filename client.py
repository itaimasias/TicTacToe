import sys
import json
import asyncio
import websockets

def print_board(board):
    print("\n")
    for row in board:
        print(" | ".join(cell if cell else " " for cell in row))
        print("--+---+--")
    print("\n")

async def play(server_url, game_id, player_id):
    async with websockets.connect(f"{server_url}/ws/{game_id}/{player_id}") as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data["type"] == "update":
                print_board(data["board"])
                if data.get("winner"):
                    if data["winner"] == "draw":
                        print("It's a draw!")
                        break
                    else:
                        print(f"Winner: {data['winner']}")
                        break
                print(f"Next turn: {data['nextTurn']}")
                while data["nextTurn"] == player_id:
                    try:
                        move = input("Enter your move as 'row col' (0-based): ").strip()
                        row, col = map(int, move.split())
                        await ws.send(json.dumps({"type": "move", "row": row, "col": col}))
                        msg2 = await ws.recv()
                        data2 = json.loads(msg2)
                        if data2["type"] == "error":
                            print("Error:", data2["message"])
                            continue
                        else:
                            msg = msg2
                            data = data2
                            break
                    except Exception:
                        print("Invalid input. Please enter as: row col")
            elif data["type"] == "win":
                print(f"Winner: {data['winner']}")
                break
            elif data["type"] == "draw":
                print("It's a draw!")
                break
            elif data["type"] == "error":
                print("Error:", data["message"])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py ws://localhost:3001 game1 X")
        exit(1)
    server_url, game_id, player_id = sys.argv[1:4]
    asyncio.run(play(server_url, game_id, player_id))
