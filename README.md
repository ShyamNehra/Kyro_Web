**Infinite Gomoku** is a sleek, modern reimagining of the classic strategy board game, completely removing the boundaries of the traditional 15x15 grid. Built with a buttery-smooth HTML5 Canvas and a real-time WebSocket backend, players can seamlessly click and drag to pan across an endless playing field to outmaneuver their opponents. 

Featuring a responsive, glassmorphism UI optimized for both desktop and mobile, you can challenge a custom-built heuristic AI that simulates human-like blunders and thinking delays, or jump into Local PvP for a classic hot-seat battle. In a game with no walls, you only run out of space when you get outsmarted.

## 📜 The Rules of the Game
The rules of Gomoku are incredibly simple to learn, but notoriously difficult to master.

* **The Objective:** Be the first player to form an unbroken chain of exactly **five** pieces horizontally, vertically, or diagonally.
* **The Gameplay:** Player X (Light) and Player O (Gold) take turns placing one piece at a time inside any empty square on the board.
* **The Infinite Board:** There are no edges. If your opponent tries to block you into a corner, simply click and drag to pan the camera and continue building your attack in the endless void.
* **Match Tracking:** The game ends immediately when a player connects 5 pieces.

**[Play the Live Demo Here](https://gomokufrontend.vercel.app/)** 
## Features
*  **Infinite Canvas:** Click and drag to explore a limitless playing field.
*  **Humanized AI:** An intelligent Python algorithm that pauses to "think" and occasionally blunders like a real player.
*  **Local PvP:** Hot-seat multiplayer with persistent session score tracking.
*  **Mobile-First Design:** Fully responsive with native-feeling touch controls and gesture lock. 
*  **Real-Time Engine:** Stateless, instant gameplay via WebSockets.

## Tech Stack
* **Frontend:** React, Vite, HTML5 Canvas
* **Backend:** Python, FastAPI, Uvicorn, WebSockets
* **Deployment:** Vercel (Frontend), Render (Backend)

## Running Locally

**1. Clone the repository**
\`\`\`bash
git clone https://github.com/ShyamNehra/gomoku_web.git
cd gomoku-web
\`\`\`

**2. Start the Backend (FastAPI)**
\`\`\`bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
uvicorn main:app --reload
\`\`\`

**3. Start the Frontend (React/Vite)**
Open a new terminal window:
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`
