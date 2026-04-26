"""
model.py — Kyro (Infinite Grid Tic-Tac-Toe) Model
MVC Architecture | Pure logic, no pygame dependency.

Board state is stored in a dictionary:
    { (x, y): 'X' | 'O' }
allowing the grid to expand infinitely in all directions.
"""

# Number of consecutive pieces required to win.
WIN_LENGTH = 5

# The four axis directions to check for a win.
# Each tuple represents (dx, dy) for one axis (we check both ± directions).
DIRECTIONS = [
    (1, 0),   # Horizontal  →
    (0, 1),   # Vertical    ↓
    (1, 1),   # Diagonal    ↘
    (1, -1),  # Diagonal    ↗
]


class GameModel:
    """
    Encapsulates all game state and logic for Kyro on an infinite grid.

    Attributes:
        board   (dict)  : Maps (x, y) tuples to 'X' or 'O'.
        current (str)   : Whose turn it is — 'X' or 'O'.
        winner  (str|None): 'X', 'O', or None if the game is still ongoing.
        game_over (bool): True once a winner has been found.
    """

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """Restore the model to its initial, empty state."""
        self.board: dict[tuple[int, int], str] = {}
        self.current: str = "X"          # X always goes first
        self.winner: str | None = None
        self.game_over: bool = False
        self.winning_line: list[tuple[int, int]] = []

    def place_piece(self, x: int, y: int) -> bool:
        """
        Attempt to place the current player's piece at (x, y).

        Returns:
            True  — the move was legal and has been applied.
            False — the cell is already occupied or the game is over.
        """
        if self.game_over:
            return False
        if (x, y) in self.board:
            return False

        # Record the move.
        self.board[(x, y)] = self.current

        # Check whether this move wins the game.
        win_coords = self.check_win(x, y, self.current)
        if win_coords:
            self.winner = self.current
            self.game_over = True
            self.winning_line = win_coords
        else:
            # Advance to the next player's turn.
            self._toggle_turn()

        return True

    def check_win(self, x: int, y: int, player: str) -> list[tuple[int, int]] | None:
        """
        Return the list of coordinates of the winning line if `player` has 
        WIN_LENGTH consecutive pieces along any axis passing through (x, y).
        Otherwise return None.
        """
        for dx, dy in DIRECTIONS:
            line = [(x, y)]
            line.extend(self._get_consecutive_coords(x, y, dx, dy, player))
            line.extend(self._get_consecutive_coords(x, y, -dx, -dy, player))

            if len(line) >= WIN_LENGTH:
                # We return exactly WIN_LENGTH pieces for the golden line.
                # Since multiple wins can happen (e.g. 6-in-a-row), 
                # we just return the first 5 found on this axis.
                return sorted(line)[:WIN_LENGTH]

        return None

    def get_cell(self, x: int, y: int) -> str | None:
        """Return the occupant of (x, y), or None if the cell is empty."""
        return self.board.get((x, y))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_consecutive_coords(
        self, x: int, y: int, dx: int, dy: int, player: str
    ) -> list[tuple[int, int]]:
        """
        Walk from (x, y) in direction (dx, dy), step by step, and return 
        the coordinates of consecutive cells belonging to `player`.
        """
        coords = []
        nx, ny = x + dx, y + dy

        while self.board.get((nx, ny)) == player:
            coords.append((nx, ny))
            nx += dx
            ny += dy

        return coords

    def _toggle_turn(self):
        """Switch the active player from 'X' to 'O' or vice‑versa."""
        self.current = "O" if self.current == "X" else "X"

    # ------------------------------------------------------------------
    # Dunder helpers (useful for debugging)
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        status = f"winner={self.winner}" if self.game_over else f"turn={self.current}"
        return f"<GameModel pieces={len(self.board)} {status}>"