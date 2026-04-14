"""
model.py — Gomoku (Infinite Grid Tic-Tac-Toe) Model
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
    Encapsulates all game state and logic for Gomoku on an infinite grid.

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
        if self.check_win(x, y, self.current):
            self.winner = self.current
            self.game_over = True
        else:
            # Advance to the next player's turn.
            self._toggle_turn()

        return True

    def check_win(self, x: int, y: int, player: str) -> bool:
        """
        Return True if `player` has WIN_LENGTH consecutive pieces along any
        axis passing through (x, y).

        Only the four axes are examined (horizontal, vertical, two diagonals).
        For each axis we count pieces in both the positive *and* negative
        directions from (x, y), then add 1 for the piece at (x, y) itself.
        """
        for dx, dy in DIRECTIONS:
            count = 1  # Count the piece just placed at (x, y).
            count += self._count_consecutive(x, y, dx, dy, player)
            count += self._count_consecutive(x, y, -dx, -dy, player)

            if count >= WIN_LENGTH:
                return True

        return False

    def get_cell(self, x: int, y: int) -> str | None:
        """Return the occupant of (x, y), or None if the cell is empty."""
        return self.board.get((x, y))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _count_consecutive(
        self, x: int, y: int, dx: int, dy: int, player: str
    ) -> int:
        """
        Walk from (x, y) in direction (dx, dy), step by step, and count how
        many consecutive cells belong to `player`.

        The starting cell (x, y) itself is *not* counted here — the caller
        is responsible for adding 1 for it.
        """
        count = 0
        nx, ny = x + dx, y + dy

        while self.board.get((nx, ny)) == player:
            count += 1
            nx += dx
            ny += dy

        return count

    def _toggle_turn(self):
        """Switch the active player from 'X' to 'O' or vice‑versa."""
        self.current = "O" if self.current == "X" else "X"

    # ------------------------------------------------------------------
    # Dunder helpers (useful for debugging)
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        status = f"winner={self.winner}" if self.game_over else f"turn={self.current}"
        return f"<GameModel pieces={len(self.board)} {status}>"
    


    #Test Block
if __name__ == "__main__":
    import traceback

    passed = 0
    failed = 0

    def run_test(name, fn):
        global passed, failed
        try:
            fn()
            print(f"  ✅ PASS — {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAIL — {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  💥 ERROR — {name}: {e}")
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 52)
    print("  Gomoku Model — Test Suite")
    print("=" * 52)

    # ── 1. Fresh board state ───────────────────────────────
    print("\n[1] Initial State")

    def test_initial_state():
        m = GameModel()
        assert m.board == {}, "Board should be empty"
        assert m.current == "X", "X should go first"
        assert m.winner is None, "No winner yet"
        assert m.game_over is False, "Game should not be over"

    run_test("initial state is clean", test_initial_state)

    # ── 2. Legal move ──────────────────────────────────────
    print("\n[2] Placing Pieces")

    def test_legal_move():
        m = GameModel()
        result = m.place_piece(0, 0)
        assert result is True, "First move should succeed"
        assert m.board[(0, 0)] == "X", "Cell (0,0) should be X"
        assert m.current == "O", "Turn should advance to O"

    run_test("legal move accepted and turn advances", test_legal_move)

    def test_occupied_cell_rejected():
        m = GameModel()
        m.place_piece(0, 0)
        result = m.place_piece(0, 0)  # same cell again
        assert result is False, "Move on occupied cell should fail"
        assert m.current == "O", "Turn should not change on illegal move"

    run_test("occupied cell is rejected", test_occupied_cell_rejected)

    def test_alternating_turns():
        m = GameModel()
        for expected in ["O", "X", "O", "X"]:
            m.place_piece(*[(i, 99) for i in range(10)].pop(0))  # unique cells
            # just check turn flips properly via a fresh sequence
        # cleaner explicit version:
        m2 = GameModel()
        m2.place_piece(0, 0)
        assert m2.current == "O"
        m2.place_piece(1, 0)
        assert m2.current == "X"
        m2.place_piece(2, 0)
        assert m2.current == "O"

    run_test("turns alternate correctly", test_alternating_turns)

    # ── 3. Win detection ───────────────────────────────────
    print("\n[3] Win Detection")

    def _make_winning_game(coords):
        """Helper: X plays coords, O plays out of the way, returns model."""
        m = GameModel()
        ox = 100  # O plays far away to not interfere
        for i, (x, y) in enumerate(coords):
            m.place_piece(x, y)
            if not m.game_over:
                m.place_piece(ox + i, 99)
        return m

    def test_horizontal_win():
        m = _make_winning_game([(i, 0) for i in range(5)])
        assert m.game_over, "Should detect horizontal win"
        assert m.winner == "X"

    run_test("horizontal 5-in-a-row", test_horizontal_win)

    def test_vertical_win():
        m = _make_winning_game([(0, i) for i in range(5)])
        assert m.game_over, "Should detect vertical win"
        assert m.winner == "X"

    run_test("vertical 5-in-a-row", test_vertical_win)

    def test_diagonal_down_right_win():
        m = _make_winning_game([(i, i) for i in range(5)])
        assert m.game_over, "Should detect diagonal (↘) win"
        assert m.winner == "X"

    run_test("diagonal ↘ 5-in-a-row", test_diagonal_down_right_win)

    def test_diagonal_up_right_win():
        m = _make_winning_game([(i, -i) for i in range(5)])
        assert m.game_over, "Should detect diagonal (↗) win"
        assert m.winner == "X"

    run_test("diagonal ↗ 5-in-a-row", test_diagonal_up_right_win)

    def test_four_in_a_row_is_not_a_win():
        m = _make_winning_game([(i, 0) for i in range(4)])
        assert not m.game_over, "4-in-a-row should NOT win"
        assert m.winner is None

    run_test("4-in-a-row is not a win", test_four_in_a_row_is_not_a_win)

    def test_win_from_middle():
        # Place X at 2,0 then fill outward: 0,1,3,4 — win closes from centre
        m = GameModel()
        moves_x = [2, 0, 1, 3, 4]  # X plays col by col; O plays away
        for i, col in enumerate(moves_x):
            m.place_piece(col, 0)
            if not m.game_over:
                m.place_piece(100 + i, 99)
        assert m.game_over, "Win should be detected even when closed from middle"
        assert m.winner == "X"

    run_test("win detected when gap is filled from middle", test_win_from_middle)

    def test_negative_coordinates():
        m = _make_winning_game([(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)])
        assert m.game_over, "Should work with negative coordinates"
        assert m.winner == "X"

    run_test("negative coordinates work correctly", test_negative_coordinates)

    # ── 4. Post-game behaviour ─────────────────────────────
    print("\n[4] Post-Game Behaviour")

    def test_no_moves_after_win():
        m = _make_winning_game([(i, 0) for i in range(5)])
        result = m.place_piece(99, 99)
        assert result is False, "No moves should be accepted after game over"

    run_test("moves blocked after win", test_no_moves_after_win)

    def test_reset():
        m = _make_winning_game([(i, 0) for i in range(5)])
        m.reset()
        assert m.board == {}
        assert m.current == "X"
        assert m.winner is None
        assert m.game_over is False

    run_test("reset clears all state", test_reset)

    # ── 5. get_cell ────────────────────────────────────────
    print("\n[5] get_cell Helper")

    def test_get_cell():
        m = GameModel()
        assert m.get_cell(0, 0) is None, "Empty cell should return None"
        m.place_piece(0, 0)
        assert m.get_cell(0, 0) == "X", "Placed cell should return 'X'"

    run_test("get_cell returns correct values", test_get_cell)

    # ── Summary ────────────────────────────────────────────
    total = passed + failed
    print("\n" + "=" * 52)
    print(f"  Results: {passed}/{total} passed", "🎉" if failed == 0 else "⚠️")
    print("=" * 52 + "\n")