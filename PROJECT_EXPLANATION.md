# Kyro: Project Deep-Dive

Welcome to **Kyro**, a modern take on the classic Tic-Tac-Toe game, expanded into an "infinite" universe. This document explains everything about how the project was built, why certain technologies were chosen, and how the "magic" happens behind the scenes.

---

## 1. The Core Concept: What is Kyro?
Most people know Tic-Tac-Toe as a 3x3 grid where you get 3-in-a-row to win. **Kyro** takes this to the next level:
- **Infinite Grid:** The board has no edges. You can pan and play as far as you want in any direction.
- **5-in-a-row (Gomoku):** Because the grid is infinite, 3-in-a-row is too easy. You need **5** consecutive pieces to win.
- **AI & PvP:** You can play against a "humanized" AI or a friend locally.

---

## 2. The Tech Stack: The "Ingredients"

### The Backend (The "Brain")
*   **Language:** Python
*   **Framework:** FastAPI
*   **Communication:** WebSockets

**Why these?**
Python is the industry standard for AI and logic. We used **FastAPI** because it is incredibly fast and has native support for **WebSockets**. 
- **Standard HTTP** (what most websites use) is like sending a letter: you send a request, and get a response. 
- **WebSockets** are like a phone call: the connection stays open, and the server can "talk" to the game instantly whenever the AI makes a move.

**Alternatives:** 
- *Node.js (Socket.io):* Very popular, but Python’s AI libraries are slightly more robust for future expansion.
- *Django:* Too "heavy" for a simple game like this. FastAPI is lightweight and "surgical."

### The Frontend (The "Face")
*   **Framework:** React 19
*   **Build Tool:** Vite
*   **Rendering:** HTML5 Canvas

**Why these?**
**React** allows us to build a user interface out of small, reusable "components." We used **Vite** because it starts up and builds the code almost instantly compared to older tools like Create React App.

The most important choice was **HTML5 Canvas**. 
- In a normal web page, every button or text is a "DOM element" (like a Lego brick). If you have 10,000 bricks, the browser gets slow. 
- **Canvas** is like a blank piece of paper where we "paint" the game 60 times every second. This allows for smooth panning across an infinite board without the browser lagging.

**Alternatives:** 
- *SVG:* Good for graphics, but gets slow with too many pieces.
- *Vanilla JavaScript:* Harder to maintain as the project grows.

---

## 3. How the AI Works: "Humanized" Heuristics

The AI isn't just "guessing." It uses a **Heuristic Scoring System**.

### How it "Thinks":
1.  **Scanning:** It looks at every empty spot near the pieces already on the board.
2.  **Scoring:** It gives each spot a score. 
    - *Is it a win for me?* (High priority)
    - *Is the human about to win? I must block!* (High priority)
    - *Is this a good setup for a future 5-in-a-row?* (Medium priority)
3.  **Humanizing:** If the AI played perfectly every time, you would always lose. We added a "mistake" algorithm. Sometimes, the AI will intentionally pick its 2nd or 3rd best move to give the player a chance, making the game more "fun" and less "robotic."

---

## 4. The "Infinite" Logic: Dictionary Coordinates

A big question for tech-minded people: **How do you store an infinite board?** 

Usually, boards are "Arrays" (a fixed list like `[0,1,2]`). But you can't have an infinite list!
Instead, we use a **Dictionary (or Hash Map)**.
- Each piece is stored as a coordinate: `(10, -500): "X"`.
- This means we only store the cells that *actually have pieces*. The empty space costs zero memory, allowing the "infinite" feel.

---

## 5. Summary of Features
| Feature | Implementation | Benefit |
| :--- | :--- | :--- |
| **Real-time Moves** | WebSockets | Zero delay between you and the server. |
| **Infinite Panning** | Canvas + Camera Logic | Explore the board freely without limits. |
| **Sound Effects** | Audio Context API | Immersive feedback for every move. |
| **Modern UI** | CSS3 + React | Sleek, "dark-mode" aesthetic that feels premium. |

---

## 6. How to Run It (For Developers)

### Backend
1. Go to `/backend`.
2. Install requirements: `pip install -r requirements.txt`.
3. Run: `python main.py` or `uvicorn main:app --reload`.

### Frontend
1. Go to `/frontend`.
2. Install dependencies: `npm install`.
3. Start development server: `npm run dev`.

---

