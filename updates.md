# Project Updates

This file tracks the latest updates and improvements made to the Infinite Gomoku project.

## [2026-04-18 14:30] - Sound Effects Integration
- **Added**: Centralized `SOUNDS` configuration and `playSound` utility.
- **Improved**: UI interaction with a `click` sound on all menu and game buttons.
- **Improved**: Gameplay immersion with a `place` sound triggered on every piece placement (Player & AI).
- **Added**: Win/Loss audio feedback tailored for both AI and Local PvP modes.

## [2026-04-18 14:15] - "How to Play" Modal & Menu Enhancement
- **Added**: "How to Play" button to the Main Menu.
- **Added**: Responsive rules overlay using glassmorphism styling.
- **Added**: Concise, human-readable rules adapted from the README:
  1. Goal: Connect exactly 5 pieces.
  2. Gameplay: Turns for X and O.
  3. Infinite Grid: Click and drag to pan.
  4. Victory: Instant win upon connecting 5.
- **Improved**: Mobile responsiveness for all menu overlays and modals.

## [2026-04-19 10:45] - Gameplay Stability & Audio Polishing
- **Fixed**: Resolved a bug where AI status messages ("AI is thinking...") would temporarily wipe the board from the screen by wrapping board updates in a conditional WebSocket check.
- **Improved**: Eliminated audio playback latency by implementing an audio preloading system with `cloneNode` playback for zero-delay sound effects.
- **Improved**: Fixed redundant "double-click" sounds on menu buttons by consolidating click-sound logic.
- **Improved**: Enhanced the Scoreboard to display in both "vs AI" and "Local PvP" modes with dynamic labels (**PLAYER** vs **AI** or **PLAYER X** vs **PLAYER O**).
- **Updated**: Standardized all audio assets to `.wav` format for consistent quality and performance.

---
*Last updated: 2026-04-19 10:50*
