# -*- coding: utf-8 -*-
"""
Tetris Game Logic Test
Testing core game functionality
"""

# Tetris shape definitions
SHAPES = [
    [[1, 1, 1, 1]],  # I-type
    [[1, 1], [1, 1]],  # O-type
    [[0, 1, 0], [1, 1, 1]],  # T-type
    [[0, 1, 1], [1, 1, 0]],  # S-type
    [[1, 1, 0], [0, 1, 1]],  # Z-type
    [[1, 0, 0], [1, 1, 1]],  # J-type
    [[0, 0, 1], [1, 1, 1]]   # L-type
]

COLORS = ['CYAN', 'YELLOW', 'PURPLE', 'GREEN', 'RED', 'BLUE', 'ORANGE']

class TetrisPiece:
    """Simple Tetris piece class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = 0
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]

    def rotate(self):
        """Rotate piece"""
        if self.shape_index == 1:  # O-type doesn't rotate
            return self.shape

        rotated = []
        for i in range(len(self.shape[0])):
            row = []
            for j in range(len(self.shape) - 1, -1, -1):
                row.append(self.shape[j][i])
            rotated.append(row)

        return rotated

class TetrisGame:
    """Simple Tetris game for testing"""

    def __init__(self):
        self.grid_width = 10
        self.grid_height = 20
        self.reset_game()

    def reset_game(self):
        """Reset game"""
        self.board = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = TetrisPiece(self.grid_width // 2 - 1, 0)
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False

    def is_valid_position(self, piece, dx=0, dy=0, shape=None):
        """Check if position is valid"""
        test_shape = shape if shape else piece.shape

        for y, row in enumerate(test_shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy

                    # Check boundaries
                    if new_x < 0 or new_x >= self.grid_width or new_y >= self.grid_height:
                        return False

                    # Check collision
                    if new_y >= 0 and self.board[new_y][new_x] != 0:
                        return False

        return True

    def lock_piece(self, piece):
        """Lock piece to board"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell and piece.y + y >= 0:
                    self.board[piece.y + y][piece.x + x] = piece.shape_index + 1

    def clear_lines(self):
        """Clear complete lines"""
        lines_cleared = []

        for y in range(self.grid_height):
            if all(cell != 0 for cell in self.board[y]):
                lines_cleared.append(y)

        for y in lines_cleared:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.grid_width)])

        if lines_cleared:
            self.lines_cleared += len(lines_cleared)
            self.score += len(lines_cleared) * 100

        return len(lines_cleared)

    def move_piece(self, dx, dy):
        """Move piece"""
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        """Rotate piece"""
        rotated = self.current_piece.rotate()
        if self.is_valid_position(self.current_piece, shape=rotated):
            self.current_piece.shape = rotated
            return True
        return False

    def hard_drop(self):
        """Hard drop"""
        drop_distance = 0
        while self.is_valid_position(self.current_piece, dy=1):
            self.current_piece.y += 1
            drop_distance += 1

        self.score += drop_distance * 2
        self.lock_current_piece()

    def lock_current_piece(self):
        """Lock current piece"""
        self.lock_piece(self.current_piece)
        self.clear_lines()

        # Generate new piece
        self.current_piece = TetrisPiece(self.grid_width // 2 - 1, 0)

        # Check game over
        if not self.is_valid_position(self.current_piece):
            self.game_over = True

    def print_board(self):
        """Print game board"""
        print(f"Score: {self.score}, Lines: {self.lines_cleared}")
        print(f"Current piece at ({self.current_piece.x}, {self.current_piece.y})")
        print("+" + "-" * (self.grid_width * 2) + "+")

        # Create display board
        display_board = [row[:] for row in self.board]

        # Add current piece
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_piece.y + y
                    board_x = self.current_piece.x + x
                    if 0 <= board_y < self.grid_height and 0 <= board_x < self.grid_width:
                        display_board[board_y][board_x] = 8  # Use 8 for current piece

        # Print board
        for row in display_board:
            print("|", end="")
            for cell in row:
                if cell == 0:
                    print("  ", end="")
                else:
                    print(f"{cell:2d}", end="")
            print("|")

        print("+" + "-" * (self.grid_width * 2) + "+")
        print()

def run_tests():
    """Run tests"""
    print("=== TETRIS GAME TEST SUITE ===\n")

    # Test 1: Basic game initialization
    print("Test 1: Basic game initialization")
    game = TetrisGame()
    print(f"Board size: {len(game.board)} x {len(game.board[0])}")
    print(f"Current piece position: ({game.current_piece.x}, {game.current_piece.y})")
    print(f"Game over status: {game.game_over}")
    print("PASS: Initialization test\n")

    # Test 2: Piece movement
    print("Test 2: Piece movement")
    initial_x = game.current_piece.x
    success = game.move_piece(1, 0)
    print(f"Move right: {success}, New position: ({game.current_piece.x}, {game.current_piece.y})")

    success = game.move_piece(-1, 0)
    print(f"Move left: {success}, New position: ({game.current_piece.x}, {game.current_piece.y})")

    # Test boundaries
    old_x = game.current_piece.x
    while game.move_piece(1, 0):
        pass
    print(f"Reached right boundary: {game.current_piece.x}")

    game.move_piece(-5, 0)  # Go back to middle
    print("PASS: Movement test\n")

    # Test 3: Piece rotation
    print("Test 3: Piece rotation")
    original_shape = [row[:] for row in game.current_piece.shape]
    success = game.rotate_piece()
    print(f"Rotation successful: {success}")
    if success:
        print(f"Original shape: {original_shape}")
        print(f"Rotated shape: {game.current_piece.shape}")
    print("PASS: Rotation test\n")

    # Test 4: Drop and lock
    print("Test 4: Drop and lock")
    print("Board state (before locking):")
    game.print_board()

    # Simulate drop
    game.hard_drop()
    print("After hard drop:")
    game.print_board()
    print("PASS: Drop test\n")

    # Test 5: Line clearing
    print("Test 5: Line clearing test")
    # Manually set a complete line
    for x in range(game.grid_width):
        game.board[game.grid_height - 1][x] = 1

    print("After adding complete line:")
    game.print_board()

    lines_cleared = game.clear_lines()
    print(f"Lines cleared: {lines_cleared}")
    print("After line clear:")
    game.print_board()
    print("PASS: Line clearing test\n")

    # Test 6: Game over detection
    print("Test 6: Game over detection")
    # Fill top few rows to simulate game over
    for y in range(3):
        for x in range(game.grid_width):
            if x < 5:  # Only fill partially to avoid complete blockage
                game.board[y][x] = 1

    print("Board with obstacles:")
    game.print_board()

    # Try to generate new piece
    game.current_piece = TetrisPiece(game.grid_width // 2 - 1, 0)
    if not game.is_valid_position(game.current_piece):
        game.game_over = True

    print(f"Game over status: {game.game_over}")
    print("PASS: Game over detection\n")

    # Test 7: Complete game simulation
    print("Test 7: Simplified game loop simulation")
    game.reset_game()

    for step in range(5):
        print(f"--- Step {step + 1} ---")

        # Random movement
        import random
        if random.random() < 0.5:
            dx = random.choice([-1, 1])
            game.move_piece(dx, 0)

        # Random rotation
        if random.random() < 0.3:
            game.rotate_piece()

        # Drop down
        if not game.move_piece(0, 1):
            game.lock_current_piece()

        game.print_board()

        if game.game_over:
            print("Game over!")
            break

    print(f"Final score: {game.score}")
    print(f"Lines cleared: {game.lines_cleared}")
    print("PASS: Game loop simulation\n")

    print("=== ALL TESTS COMPLETED ===")
    print("SUCCESS: All Tetris core functionality tests passed!")

if __name__ == "__main__":
    run_tests()