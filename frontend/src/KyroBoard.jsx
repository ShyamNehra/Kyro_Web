import { useEffect, useRef, useCallback, useState } from "react";

// ── Constants ──────────────────────────────────────────────────────────────
const CELL_SIZE      = 48;
const WS_URL         = "wss://gomoku-backend-v3wc.onrender.com/ws/game";
const PIECE_RADIUS   = CELL_SIZE * 0.38;
const DRAG_THRESHOLD = 10;

// ── Theme ──────────────────────────────────────────────────────────────────
const THEME = {
  bg:            "#0d0f14",
  gridLine:      "rgba(255,255,255,0.07)",
  gridLineMajor: "rgba(255,255,255,0.13)",
  dot:           "rgba(255,255,255,0.18)",
  dotCenter:     "#e8b84b",
  vignette:      "rgba(13,15,20,0.55)",
  crosshairH:    "rgba(232,184,75,0.06)",
  crosshairV:    "rgba(232,184,75,0.06)",
  cursor:        "crosshair",
  cursorPan:     "grabbing",
  pieceXGlow:    "rgba(140,170,255,0.30)",
  pieceOGlow:    "rgba(232,184,75,0.22)",
  pieceXStroke:  "rgba(150,180,255,0.5)",
  pieceOStroke:  "rgba(232,184,75,0.7)",
  pieceXText:    "#0d0f14",
  pieceOText:    "#e8b84b",
  ghostFill:     "rgba(232,184,75,0.07)",
  ghostStroke:   "rgba(232,184,75,0.28)",
};

// ── Sounds ─────────────────────────────────────────────────────────────────
const SOUNDS = {
  click: "/sounds/click.wav",
  place: "/sounds/place.wav",
  win:   "/sounds/win.wav",
  lose:  "/sounds/lose.wav",
};

const AUDIO_INSTANCES = {};
if (typeof window !== "undefined") {
  for (const [key, path] of Object.entries(SOUNDS)) {
    const audio = new Audio(path);
    audio.preload = "auto";
    AUDIO_INSTANCES[key] = audio;
  }
}

const playSound = (type) => {
  const instance = AUDIO_INSTANCES[type];
  if (!instance) return;
  const audio = instance.cloneNode(true);
  audio.play().catch(() => {}); // Catch browser-blocked autoplay
};

// ── Pure drawing helpers ───────────────────────────────────────────────────
const snap = (v) => Math.round(v);

function drawDot(ctx, cx, cy, radius, color) {
  ctx.beginPath();
  ctx.arc(snap(cx), snap(cy), radius, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
}

function drawVignette(ctx, w, h, color) {
  const g = ctx.createRadialGradient(
    w / 2, h / 2, Math.min(w, h) * 0.3,
    w / 2, h / 2, Math.max(w, h) * 0.78,
  );
  g.addColorStop(0, "transparent");
  g.addColorStop(1, color);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);
}

function drawPiece(ctx, cx, cy, player) {
  const r = PIECE_RADIUS;
  const isX = player === "X";

  const halo = ctx.createRadialGradient(cx, cy, r * 0.4, cx, cy, r * 1.7);
  halo.addColorStop(0, isX ? THEME.pieceXGlow : THEME.pieceOGlow);
  halo.addColorStop(1, "transparent");
  ctx.fillStyle = halo;
  ctx.beginPath();
  ctx.arc(snap(cx), snap(cy), r * 1.7, 0, Math.PI * 2);
  ctx.fill();

  const body = ctx.createRadialGradient(
    cx - r * 0.28, cy - r * 0.28, r * 0.05,
    cx, cy, r,
  );
  if (isX) {
    body.addColorStop(0, "#ffffff");
    body.addColorStop(1, "#b8c8f0");
  } else {
    body.addColorStop(0, "#2a2f42");
    body.addColorStop(1, "#0d0f14");
  }
  ctx.beginPath();
  ctx.arc(snap(cx), snap(cy), r, 0, Math.PI * 2);
  ctx.fillStyle = body;
  ctx.fill();

  ctx.strokeStyle = isX ? THEME.pieceXStroke : THEME.pieceOStroke;
  ctx.lineWidth   = isX ? 1 : 1.5;
  ctx.stroke();

  ctx.fillStyle    = isX ? THEME.pieceXText : THEME.pieceOText;
  ctx.font         = `bold ${Math.round(r * 0.9)}px 'DM Mono','Fira Mono',monospace`;
  ctx.textAlign    = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(player, snap(cx), snap(cy) + 1);
}

// ── Master render function ─────────────────────────────────────────────────
function render(canvas, camera, board, hover, myTurn, appState, winningLine) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const W   = canvas.width  / dpr;
  const H   = canvas.height / dpr;

  ctx.save();
  ctx.scale(dpr, dpr);

  ctx.fillStyle = THEME.bg;
  ctx.fillRect(0, 0, W, H);

  const ox = camera.x;
  const oy = camera.y;

  ctx.fillStyle = THEME.crosshairV;
  ctx.fillRect(snap(ox), 0, CELL_SIZE, H);
  ctx.fillStyle = THEME.crosshairH;
  ctx.fillRect(0, snap(oy), W, CELL_SIZE);

  const firstCol = Math.floor(-ox / CELL_SIZE) - 1;
  const lastCol  = Math.ceil((W - ox) / CELL_SIZE) + 1;
  const firstRow = Math.floor(-oy / CELL_SIZE) - 1;
  const lastRow  = Math.ceil((H - oy) / CELL_SIZE) + 1;

  ctx.lineWidth = 0.5;
  for (let col = firstCol; col <= lastCol; col++) {
    const x = snap(ox + col * CELL_SIZE);
    ctx.strokeStyle = col % 5 === 0 ? THEME.gridLineMajor : THEME.gridLine;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
  }
  for (let row = firstRow; row <= lastRow; row++) {
    const y = snap(oy + row * CELL_SIZE);
    ctx.strokeStyle = row % 5 === 0 ? THEME.gridLineMajor : THEME.gridLine;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }

  for (let col = firstCol; col <= lastCol; col++) {
    for (let row = firstRow; row <= lastRow; row++) {
      if (col === 0 && row === 0) continue;
      const r = col % 5 === 0 && row % 5 === 0 ? 2.2 : 1.2;
      drawDot(ctx, ox + col * CELL_SIZE, oy + row * CELL_SIZE, r, THEME.dot);
    }
  }

  const c0x = ox + CELL_SIZE / 2;
  const c0y = oy + CELL_SIZE / 2;
  const glow = ctx.createRadialGradient(c0x, c0y, 0, c0x, c0y, 30);
  glow.addColorStop(0, "rgba(232,184,75,0.15)");
  glow.addColorStop(1, "transparent");
  ctx.fillStyle = glow;
  ctx.fillRect(ox, oy, CELL_SIZE, CELL_SIZE);

  drawVignette(ctx, W, H, THEME.vignette);

  for (const [key, player] of Object.entries(board)) {
    const [gx, gy] = key.split(",").map(Number);
    const cx = ox + gx * CELL_SIZE + CELL_SIZE / 2;
    const cy = oy + gy * CELL_SIZE + CELL_SIZE / 2;
    if (cx < -CELL_SIZE || cx > W + CELL_SIZE) continue;
    if (cy < -CELL_SIZE || cy > H + CELL_SIZE) continue;
    drawPiece(ctx, cx, cy, player);
  }

  // ── DRAW WINNING LINE ──
  if (winningLine && winningLine.length >= 5) {
    ctx.beginPath();
    winningLine.forEach(([gx, gy], i) => {
      const cx = ox + gx * CELL_SIZE + CELL_SIZE / 2;
      const cy = oy + gy * CELL_SIZE + CELL_SIZE / 2;
      if (i === 0) ctx.moveTo(cx, cy);
      else ctx.lineTo(cx, cy);
    });
    
    // Golden Glow
    ctx.shadowBlur = 15;
    ctx.shadowColor = "#e8b84b";
    ctx.strokeStyle = "#e8b84b";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();
    
    // Core line
    ctx.shadowBlur = 0;
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  if (appState === "PLAYING" && myTurn && hover && !board[`${hover.gx},${hover.gy}`]) {
    const cx = ox + hover.gx * CELL_SIZE + CELL_SIZE / 2;
    const cy = oy + hover.gy * CELL_SIZE + CELL_SIZE / 2;
    ctx.beginPath();
    ctx.arc(snap(cx), snap(cy), PIECE_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle   = THEME.ghostFill;
    ctx.fill();
    ctx.strokeStyle = THEME.ghostStroke;
    ctx.lineWidth   = 1.5;
    ctx.stroke();
  }

  ctx.restore();
}

/** Canvas-pixel → nearest grid cell. */
function pixelToGrid(px, py, camera) {
  return {
    gx: Math.floor((px - camera.x) / CELL_SIZE),
    gy: Math.floor((py - camera.y) / CELL_SIZE),
  };
}

// ── Component ──────────────────────────────────────────────────────────────
export default function KyroBoard() {
  const canvasRef  = useRef(null);
  const cameraRef  = useRef({ x: 0, y: 0 });
  const dragRef    = useRef(null);
  const rafRef     = useRef(null);
  const wsRef      = useRef(null);
  const boardRef   = useRef({});
  const winningLineRef = useRef([]);
  const hoverRef   = useRef(null);
  const myTurnRef  = useRef(true);

  // Scoreboard Refs & State
  const matchScoredRef = useRef(false);
  const [scores, setScores] = useState({ X: 0, O: 0 });

  const [appState, setAppState] = useState("MENU");
  const appStateRef = useRef("MENU"); 

  const [showRules, setShowRules] = useState(false);

  const [gameMode, setGameMode] = useState("ai");
  const gameModeRef = useRef("ai");
  
  const [status,    setStatus]    = useState("Connecting…");
  const [connected, setConnected] = useState(false);
  const [message,   setMessage]   = useState("");
  const [gameOver,  setGameOver]  = useState(false);

  const changeState = useCallback((newState) => {
    playSound("click");
    appStateRef.current = newState;
    setAppState(newState);
  }, []);

  // ── Scheduling ────────────────────────────────────────────────────────
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (canvas) render(canvas, cameraRef.current, boardRef.current, hoverRef.current, myTurnRef.current, appStateRef.current, winningLineRef.current);
  }, []);

  const scheduleDraw = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(draw);
  }, [draw]);

  // ── Resize ────────────────────────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const onResize = () => {
      const dpr = window.devicePixelRatio || 1;
      const W   = window.innerWidth;
      const H   = window.innerHeight;
      canvas.width        = W * dpr;
      canvas.height       = H * dpr;
      canvas.style.width  = `${W}px`;
      canvas.style.height = `${H}px`;
      if (!cameraRef.current._initialised) {
        cameraRef.current.x = (W / 2) - (CELL_SIZE / 2);
        cameraRef.current.y = H / 2;
        cameraRef.current._initialised = true;
      }
      scheduleDraw();
    };
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [scheduleDraw]);

  // ── WebSocket ─────────────────────────────────────────────────────────
  useEffect(() => {
    let ws;
    let reconnectTimer;

    function connect() {
      ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setStatus("Connected");
        // Ensure mode is synced as soon as connection is established
        ws.send(JSON.stringify({ action: "sync_mode", mode: gameModeRef.current }));
      };

      ws.onclose = () => {
        setConnected(false);
        setStatus("Disconnected — retrying in 3 s…");
        reconnectTimer = setTimeout(connect, 3000);
      };

      ws.onerror = () => setStatus("Connection error");

      ws.onmessage = (evt) => {
        let data;
        try { data = JSON.parse(evt.data); } catch { return; }
        if (data.error) { setMessage(`⚠ ${data.error}`); return; }

        if (data.board !== undefined) {
          const prevCount = Object.keys(boardRef.current).length;
          boardRef.current = data.board;
          const newCount = Object.keys(boardRef.current).length;

          if (newCount > prevCount) {
            playSound("place");
          }

          if (gameModeRef.current === "pvp") {
            myTurnRef.current = !data.game_over;
          } else {
            myTurnRef.current = !data.game_over && data.current_turn === "X";
          }
        }

        if (data.winning_line !== undefined) {
          winningLineRef.current = data.winning_line;
        }

        // --- SCORE TRACKING LOGIC ---
        if (data.game_over && !matchScoredRef.current) {
          if (data.winner === "X") {
            setScores(s => ({ ...s, X: s.X + 1 }));
            playSound("win");
          } else if (data.winner === "O") {
            setScores(s => ({ ...s, O: s.O + 1 }));
            // In AI mode, O winning is a loss for the player.
            // In PvP mode, O winning is still a "win" for player O.
            if (gameModeRef.current === "ai") playSound("lose");
            else playSound("win");
          }
          matchScoredRef.current = true; // Lock it so it doesn't double count!
        }

        if (data.game_over) {
          // Delay the popup by 1 second
          setTimeout(() => {
            setGameOver(true);
          }, 1000);
        } else {
          setGameOver(false);
          // If board is empty (reset), clear winning line
          if (Object.keys(boardRef.current).length === 0) {
            winningLineRef.current = [];
          }
        }

        setMessage(data.message ?? "");
        scheduleDraw();
      };
    }

    connect();
    return () => { clearTimeout(reconnectTimer); ws?.close(); };
  }, [scheduleDraw]); 

  // ── Game Actions ──────────────────────────────────────────────────────
  const startGame = useCallback((mode) => {
    if (gameModeRef.current !== mode) {
      setScores({ X: 0, O: 0 }); // Reset score if switching between AI and PvP
    }
    gameModeRef.current = mode;
    matchScoredRef.current = false; // Unlock score for new round
    
    setGameMode(mode);
    changeState("PLAYING");
    setGameOver(false);
    winningLineRef.current = [];

    // Only send if socket is open; if not, ws.onopen will sync the mode later
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "reset", mode }));
    }
  }, [changeState]);

  const resetGame = useCallback(() => {
    matchScoredRef.current = false; // Unlock score for new round
    changeState("PLAYING");
    setGameOver(false);
    winningLineRef.current = [];

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "reset", mode: gameModeRef.current }));
    }
  }, [changeState]);

  const sendMove = useCallback((gx, gy) => {
    if (appStateRef.current !== "PLAYING") return; 
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!myTurnRef.current) return;
    if (boardRef.current[`${gx},${gy}`]) return;
    
    ws.send(JSON.stringify({ action: "place", x: gx, y: gy }));
  }, []);

  // ── Pointer events ────────────────────────────────────────────────────
  const onPointerDown = useCallback((e) => {
    dragRef.current = {
      startX: e.clientX, startY: e.clientY,
      camX: cameraRef.current.x, camY: cameraRef.current.y,
      moved: false,
    };
    canvasRef.current.setPointerCapture(e.pointerId);
  }, []);

  const onPointerMove = useCallback((e) => {
    const { gx, gy } = pixelToGrid(e.clientX, e.clientY, cameraRef.current);
    const changed = !hoverRef.current
      || hoverRef.current.gx !== gx
      || hoverRef.current.gy !== gy;
    hoverRef.current = { gx, gy };

    if (!dragRef.current) {
      if (changed) scheduleDraw();
      return;
    }

    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;

    if (!dragRef.current.moved && Math.hypot(dx, dy) > DRAG_THRESHOLD) {
      dragRef.current.moved = true;
      canvasRef.current.style.cursor = THEME.cursorPan;
    }
    if (dragRef.current.moved) {
      cameraRef.current.x = dragRef.current.camX + dx;
      cameraRef.current.y = dragRef.current.camY + dy;
      scheduleDraw();
    }
  }, [scheduleDraw]);

  const onPointerUp = useCallback((e) => {
    canvasRef.current.style.cursor = THEME.cursor;
    if (!dragRef.current) return;
    if (!dragRef.current.moved) {
      const { gx, gy } = pixelToGrid(e.clientX, e.clientY, cameraRef.current);
      sendMove(gx, gy);
    }
    dragRef.current = null;
  }, [sendMove]);

  const onPointerLeave = useCallback(() => {
    hoverRef.current = null;
    scheduleDraw();
    if (dragRef.current) {
      dragRef.current = null;
      canvasRef.current.style.cursor = THEME.cursor;
    }
  }, [scheduleDraw]);

  useEffect(() => () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); }, []);

  // ── JSX ───────────────────────────────────────────────────────────────
  return (
    <>
      <style>{`
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body, #root { width: 100%; height: 100%; background: #0d0f14; overflow: hidden; }
        .kyro-wrapper { position: fixed; inset: 0; overflow: hidden; }
        canvas { display: block; }

        .hud {
          font-family: 'DM Mono', 'Fira Mono', monospace;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          pointer-events: none;
          user-select: none;
          position: fixed;
        }

        .kyro-label {
          top: 55px; left: 50%; transform: translateX(-50%);
          font-size: 11px;
          color: rgba(232,184,75,0.55);
        }

        /* ── SCOREBOARD CSS ── */
        .scoreboard {
          top: 85px; left: 50%; transform: translateX(-50%);
          display: flex; align-items: center; gap: 20px;
          background: rgba(13,15,20,0.78);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 12px; padding: 8px 24px;
          backdrop-filter: blur(6px);
        }
        .score-box { display: flex; flex-direction: column; align-items: center; }
        .score-label { font-size: 8px; color: rgba(255,255,255,0.4); letter-spacing: 0.2em; margin-bottom: 2px;}
        .score-val { font-size: 16px; font-weight: bold; }
        .score-x { color: #b8c8f0; } /* Matches White/Blue pieces */
        .score-o { color: #e8b84b; } /* Matches Gold pieces */
        .score-div { color: rgba(255,255,255,0.15); font-size: 14px; }

        .conn-pill {
          top: 20px; right: 24px;
          display: flex; align-items: center; gap: 6px;
          background: rgba(13,15,20,0.78);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 999px;
          padding: 5px 14px 5px 10px;
          backdrop-filter: blur(6px);
        }
        .conn-dot {
          width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
          transition: background 0.35s, box-shadow 0.35s;
        }
        .conn-dot.on  { background: #4ade80; box-shadow: 0 0 7px #4ade80; }
        .conn-dot.off { background: #f87171; box-shadow: 0 0 7px #f87171; }
        .conn-text { font-size: 9px; color: rgba(255,255,255,0.38); }

        .pause-btn {
          position: fixed; top: 20px; left: 24px;
          font-family: 'DM Mono', 'Fira Mono', monospace;
          font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
          color: rgba(255,255,255,0.5);
          background: rgba(13,15,20,0.78);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 999px; padding: 6px 16px; cursor: pointer;
          backdrop-filter: blur(6px); transition: all 0.2s;
        }
        .pause-btn:hover { color: #fff; background: rgba(255,255,255,0.05); }

        .msg-bar {
          bottom: 58px; left: 50%; transform: translateX(-50%);
          font-size: 10px; color: rgba(255,255,255,0.32);
          white-space: nowrap;
        }

        .kyro-badge {
          bottom: 24px; right: 28px;
          font-size: 10px; color: rgba(255,255,255,0.12);
        }

        .overlay-container {
          position: fixed; inset: 0;
          background: rgba(13,15,20,0.6);
          backdrop-filter: blur(8px);
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          z-index: 100;
        }
        
        .menu-box {
          display: flex; flex-direction: column; gap: 16px;
          background: rgba(13,15,20,0.9);
          border: 1px solid rgba(232,184,75,0.28);
          border-radius: 12px; padding: 40px;
          text-align: center;
          box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }

        .menu-title {
          font-family: 'DM Mono', 'Fira Mono', monospace;
          font-size: 16px; letter-spacing: 0.2em; text-transform: uppercase;
          color: #e8b84b; margin-bottom: 10px;
        }

        .menu-btn {
          font-family: 'DM Mono', 'Fira Mono', monospace;
          font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase;
          color: rgba(255,255,255,0.8);
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 6px; padding: 12px 24px; cursor: pointer;
          transition: all 0.2s;
        }
        .menu-btn:hover {
          color: #e8b84b; border-color: rgba(232,184,75,0.5);
          background: rgba(232,184,75,0.05);
        }
        .menu-btn.accent {
          color: #13151c; background: #e8b84b; border-color: #e8b84b; font-weight: bold;
        }
        .menu-btn.accent:hover {
          background: #f0c868; box-shadow: 0 0 15px rgba(232,184,75,0.4);
        }
win
        .rules-list {
          text-align: left;
          margin: 20px 0;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .rules-item {
          display: flex;
          gap: 12px;
          font-family: 'DM Mono', 'Fira Mono', monospace;
          font-size: 13px;
          line-height: 1.6;
          color: rgba(255,255,255,0.7);
          text-align: left;
        }
        .rules-bullet {
          color: #e8b84b;
          font-weight: bold;
          flex-shrink: 0;
        }
        @media (max-width: 600px) {
          .menu-box { padding: 30px 20px; width: 92%; }
          .menu-title { font-size: 15px; }
          .rules-item { font-size: 12px; }
        }
      `}</style>

      <div className="kyro-wrapper">
        <canvas
          ref={canvasRef}
          style={{ cursor: THEME.cursor, touchAction: "none" }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerLeave}
        />

        <div className="hud kyro-label">kyro · infinite grid</div>

        {/* ── THE NEW SCOREBOARD ── */}
        {appState === "PLAYING" && (
          <div className="hud scoreboard">
            <div className="score-box">
              <span className="score-label">{gameMode === "ai" ? "PLAYER" : "PLAYER X"}</span>
              <span className="score-val score-x">{scores.X}</span>
            </div>
            <span className="score-div">-</span>
            <div className="score-box">
              <span className="score-label">{gameMode === "ai" ? "AI" : "PLAYER O"}</span>
              <span className="score-val score-o">{scores.O}</span>
            </div>
          </div>
        )}

        <div className="hud conn-pill">
          <span className={`conn-dot ${connected ? "on" : "off"}`} />
          <span className="conn-text">{status}</span>
        </div>

        {appState === "PLAYING" && !gameOver && (
          <button className="pause-btn" onClick={() => changeState("PAUSED")}>
            || Pause
          </button>
        )}

        {message && !gameOver && appState === "PLAYING" && (
          <div className="hud msg-bar">{message}</div>
        )}

        <div className="hud kyro-badge">drag to pan · click to play</div>

        {appState === "MENU" && !showRules && (
          <div className="overlay-container">
            <div className="menu-box">
              <div className="menu-title">Select Mode</div>
              <button className="menu-btn accent" onClick={() => startGame("ai")}>Play vs AI</button>
              <button className="menu-btn" onClick={() => startGame("pvp")}>Local PvP</button>
              <button className="menu-btn" onClick={() => { playSound("click"); setShowRules(true); }}>How to Play</button>
            </div>
          </div>
        )}

        {showRules && (
          <div className="overlay-container">
            <div className="menu-box">
              <div className="menu-title">How to Play</div>
              <div className="rules-list">
                <div className="rules-item">
                  <span className="rules-bullet">01</span>
                  <span>Connect exactly five pieces in a row — horizontally, vertically, or diagonally.</span>
                </div>
                <div className="rules-item">
                  <span className="rules-bullet">02</span>
                  <span>Players take turns placing one piece at a time in any empty square.</span>
                </div>
                <div className="rules-item">
                  <span className="rules-bullet">03</span>
                  <span>The board is infinite. Click and drag to pan the camera across the grid.</span>
                </div>
                <div className="rules-item">
                  <span className="rules-bullet">04</span>
                  <span>The game ends immediately when a player completes a chain of five.</span>
                </div>
              </div>
              <button className="menu-btn accent" onClick={() => { playSound("click"); setShowRules(false); }}>Got it</button>
            </div>
          </div>
        )}

        {appState === "PAUSED" && (
          <div className="overlay-container">
            <div className="menu-box">
              <div className="menu-title">Paused</div>
              <button className="menu-btn accent" onClick={() => changeState("PLAYING")}>Resume</button>
              <button className="menu-btn" onClick={resetGame}>Restart Match</button>
              <button className="menu-btn" onClick={() => changeState("MENU")}>Main Menu</button>
            </div>
          </div>
        )}

        {gameOver && appState === "PLAYING" && (
          <div className="overlay-container">
            <div className="menu-box">
              <div className="menu-title">{message}</div>
              <button className="menu-btn accent" onClick={resetGame}>Play Again</button>
              <button className="menu-btn" onClick={() => changeState("MENU")}>Main Menu</button>
            </div>
          </div>
        )}

      </div>
    </>
  );
}