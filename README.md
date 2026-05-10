#  Kyro

**[Play the Live Demo Here](https://kyro-go.vercel.app/)**

**Kyro** is a sleek, modern reimagining of classic strategy board games. It offers a dual-experience: a rigorous, perfect-play **Classic 3x3 Tic-Tac-Toe** and a boundary-defying **Infinite Gomoku**. Built with a buttery-smooth HTML5 Canvas and a real-time WebSocket backend, Kyro combines premium aesthetics with deep tactical gameplay.

Featuring a responsive, glassmorphism UI optimized for both desktop and mobile, you can challenge custom-built AIs or jump into Local PvP for a classic hot-seat battle. In a game with no walls (Infinite Mode), you only run out of space when you get outsmarted.

## 🎮 Game Modes

### 1. Classic 3x3 (Tic-Tac-Toe)
Standard Tic-Tac-Toe on a fixed grid.
* **Objective:** Get 3 in a row to win.
* **AI Opponent:** Challenge a perfect-play **Minimax AI** that never misses a beat.
* **Local PvP:** Play against a friend on the same device.

### 2. Infinite Gomoku (Five-in-a-Row)
Five-in-a-row on an endless playing field.
* **Objective:** Form an unbroken chain of exactly **five** pieces horizontally, vertically, or diagonally.
* **Infinite Board:** There are no edges. Click and drag to pan the camera across the grid.
* **Humanized AI:** An intelligent Python algorithm that pauses to "think" and simulates human-like strategy.
* **Match Tracking:** Persistent session score tracking for long-running battles.

## ✨ Features
*  **Dynamic Navigation:** A full screen-based menu system with dedicated modes for play, rules, and settings.
*  **Master Volume Control:** Global volume settings that persist across all game modes and sound effects.
*  **Infinite Canvas:** Click and drag to explore a limitless playing field in Gomoku mode.
*  **Dual-AI Systems:** From perfect-play Minimax (3x3) to humanized heuristic algorithms (Infinite).
*  **Local PvP:** Hot-seat multiplayer with persistent session score tracking.
*  **Mobile-First Design:** Fully responsive with native-feeling touch controls and gesture support.
*  **Premium Aesthetics:** Minimalist dark theme with glowing gold accents and DM Mono typography.

## 🛠️ Tech Stack
* **Frontend:** React, Vite, HTML5 Canvas, Vanilla CSS
* **Backend:** Python, FastAPI, Uvicorn, WebSockets
* **Deployment:** Vercel (Frontend), Render (Backend)

## 🚀 Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/ShyamNehra/kyro_web.git
cd kyro-web
```

**2. Start the Backend (FastAPI)**
```bash
cd backend
python -m venv .venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

**3. Start the Frontend (React/Vite)**
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
