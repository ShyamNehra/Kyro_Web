# Infinite Gomoku

A modern, boundless take on the classic game of Gomoku. Drop stones, pan across an infinite canvas, and connect five-in-a-row against a human-like AI or a friend in local PvP.

**[Play the Live Demo Here](https://your-vercel-link-here.vercel.app/)** ## Features
* 🌌 **Infinite Canvas:** Click and drag to explore a limitless playing field.
* 🤖 **Humanized AI:** An intelligent Python algorithm that pauses to "think" and occasionally blunders like a real player.
* ⚔️ **Local PvP:** Hot-seat multiplayer with persistent session score tracking.
* 📱 **Mobile-First Design:** Fully responsive with native-feeling touch controls and gesture lock. 
* ⚡ **Real-Time Engine:** Stateless, instant gameplay via WebSockets.

## Tech Stack
* **Frontend:** React, Vite, HTML5 Canvas
* **Backend:** Python, FastAPI, Uvicorn, WebSockets
* **Deployment:** Vercel (Frontend), Render (Backend)

## Running Locally

**1. Clone the repository**
\`\`\`bash
git clone https://github.com/your-username/gomoku-web.git
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
