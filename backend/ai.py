"""
ai.py — Humanized Heuristic AI for Infinite Gomoku
Evaluates the board and picks a move. Includes intentional "mistakes" 
to simulate human error and make the game fun.
"""

import random

# ── Heuristic Scoring Weights ──────────────────────────────────────────────
# How much the AI values certain board states. 
SCORE_WIN         = 100000  # 5-in-a-row (Must take immediately)
SCORE_BLOCK_WIN   = 50000   # Opponent has 4-in-a-row (Must block)
SCORE_OPEN_FOUR   = 10000   # 4-in-a-row with open ends
SCORE_BLOCK_OPEN3 = 5000    # Opponent has 3-in-a-row with open ends
SCORE_OPEN_THREE  = 1000    # 3-in-a-row with open ends
SCORE_BLOCK_TWO   = 500     # Opponent has 2-in-a-row
SCORE_TWO         = 100     # 2-in-a-row
SCORE_CENTER      = 10      # General proximity to other pieces

# Directions to check: Horizontal, Vertical, Diagonal Right, Diagonal Left
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

def get_best_move(board: dict[tuple[int, int], str], ai_player: str) -> tuple[int, int]:
    """
    Scans the board, scores available moves, and picks one.
    Simulates human error by occasionally picking the 2nd or 3rd best move.
    """
    human_player = "X" if ai_player == "O" else "O"

    # Edge Case: If the board is completely empty, play in the center.
    if not board:
        return (0, 0)

    # 1. Find all candidate moves (empty spaces adjacent to existing pieces)
    candidates = _get_candidate_moves(board)

    # 2. Score every candidate
    scored_moves = []
    for x, y in candidates:
        score = _evaluate_move(board, x, y, ai_player, human_player)
        scored_moves.append((score, (x, y)))

    # Sort moves from highest score to lowest
    scored_moves.sort(reverse=True, key=lambda item: item[0])

    if not scored_moves:
        return (0, 0)  # Fallback

    top_score = scored_moves[0][0]

    # 3. Apply "Humanized" Blurring (Mistake Probability)
    # Rule: NEVER blunder a guaranteed win or a critical block.
    if top_score >= SCORE_BLOCK_WIN:
        return scored_moves[0][1]

    # Otherwise, introduce a chance to make a suboptimal play
    roll = random.random()
    
    # Only consider up to the top 5 moves to ensure it doesn't make a completely random, terrible move
    top_moves = scored_moves[:5] 
    
    # --- THE DIFFICULTY DIALS ---
    if roll < 0.40 or len(top_moves) == 1:
        # EASY MODE: Only a 40% chance to play the perfect move
        selected_move = top_moves[0][1]
    elif roll < 0.70 and len(top_moves) >= 2:
        # EASY MODE: 30% chance it picks the 2nd best move
        selected_move = top_moves[1][1]
    else:
        # EASY MODE: 30% chance it completely blunders and misses a setup
        selected_move = top_moves[-1][1]

    return selected_move

def _get_candidate_moves(board: dict[tuple[int, int], str]) -> set[tuple[int, int]]:
    """
    Returns a set of empty (x, y) coordinates that are within 
    a 2-cell radius of any currently placed piece.
    This prevents the AI from scanning infinity.
    """
    candidates = set()
    for (px, py) in board.keys():
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = px + dx, py + dy
                if (cx, cy) not in board:
                    candidates.add((cx, cy))
    return candidates

def _evaluate_move(board: dict, x: int, y: int, ai_player: str, human_player: str) -> int:
    """Scores how good placing a piece at (x, y) would be."""
    total_score = 0

    for dx, dy in DIRECTIONS:
        ai_line = _count_line(board, x, y, dx, dy, ai_player)
        human_line = _count_line(board, x, y, dx, dy, human_player)

        # Evaluate offensive potential (AI completing its own lines)
        total_score += _score_line(ai_line[0], ai_line[1], is_offensive=True)
        
        # Evaluate defensive potential (AI blocking the human's lines)
        total_score += _score_line(human_line[0], human_line[1], is_offensive=False)

    return total_score

def _count_line(board: dict, x: int, y: int, dx: int, dy: int, player: str) -> tuple[int, int]:
    """
    Looks in both directions along a line.
    Returns (consecutive_pieces, open_ends).
    """
    consecutive = 1  # Assume we place a piece at (x,y)
    open_ends = 0

    # Check forward direction
    step = 1
    while board.get((x + dx * step, y + dy * step)) == player:
        consecutive += 1
        step += 1
    if board.get((x + dx * step, y + dy * step)) is None:
        open_ends += 1

    # Check backward direction
    step = 1
    while board.get((x - dx * step, y - dy * step)) == player:
        consecutive += 1
        step += 1
    if board.get((x - dx * step, y - dy * step)) is None:
        open_ends += 1

    return consecutive, open_ends

def _score_line(consecutive: int, open_ends: int, is_offensive: bool) -> int:
    """Assigns a point value to a specific line configuration."""
    if consecutive >= 5:
        return SCORE_WIN if is_offensive else SCORE_BLOCK_WIN
    
    if consecutive == 4:
        if open_ends > 0:
            return SCORE_OPEN_FOUR if is_offensive else SCORE_BLOCK_WIN
    
    if consecutive == 3:
        if open_ends == 2:
            return SCORE_OPEN_THREE if is_offensive else SCORE_BLOCK_OPEN3
        elif open_ends == 1:
            return SCORE_TWO if is_offensive else SCORE_BLOCK_TWO
            
    if consecutive == 2:
        if open_ends == 2:
            return SCORE_TWO if is_offensive else SCORE_BLOCK_TWO
            
    return SCORE_CENTER