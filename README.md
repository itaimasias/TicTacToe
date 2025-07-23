# TicTacToe



\# Real-Time Tic-Tac-Toe over Two Servers



\## Overview



This project implements a real-time, multiplayer Tic-Tac-Toe game, where two CLI-based clients can play against each other while being connected to different backend servers. Game state synchronization is handled in real-time using Redis Pub/Sub.



\## Architecture and Design



\- \*\*Two independent backend servers\*\* (`server.py`)  

&nbsp; Each server runs as a standalone FastAPI WebSocket server (can run on any port, e.g., 3001 and 3002).



\- \*\*Real-time synchronization\*\*  

&nbsp; Game state (board, turn, win/draw) is broadcast using Redis Pub/Sub. Whenever a move is made, all servers are updated instantly.



\- \*\*Game logic\*\*  

&nbsp; Managed by `game.py`, which handles move validation, win/draw detection, and board updates.



\- \*\*CLI WebSocket Client\*\* (`client.py`)  

&nbsp; Each player runs a terminal-based client that connects to any backend server via WebSocket, displays the ASCII game board, accepts user moves, and shows the opponent's moves in real time.



\## How to Run



\### 1. Prerequisites



\- Python 3.9+ (tested on Python 3.12)

\- \[Redis server](https://redis.io/) running locally (default: port 6379)



\### 2. Install dependencies



```bash

pip install -r requirements.txt



\# Terminal 1

set PORT=3001 \&\& python server.py

\# Terminal 2

set PORT=3002 \&\& python server.py





\# Player X connects to server A

python client.py ws://localhost:3001 game1 X



\# Player O connects to server B

python client.py ws://localhost:3002 game1 O

```



AI Tools Usage Statement

AI (OpenAI ChatGPT-4o) was used in limited areas during the assignment:



For generating the initial boilerplate for Redis pub/sub communication between servers.



For resolving specific bugs and improving error handling.



For drafting and writing this README file.



All the main game logic, validation, modular structure, and most of the implementation were written and refined by me.

