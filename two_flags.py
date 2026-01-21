"""
Two Flags Game - AI Agent
Course: Introduction to Artificial Intelligence (CS-203-3610)
A pawn-only chess variant where the goal is to reach the opposite side first
"""

import copy
import time
import random

# Constants
BOARD_SIZE = 8
WHITE = 'W'
BLACK = 'B'
EMPTY = '.'

# Piece values and position values for evaluation
PAWN_VALUE = 100
WIN_VALUE = 10000

class GameState:
    def __init__(self):
        # Board is 8x8, represented as list of lists
        # Row 0 is rank 1 (white's back), Row 7 is rank 8 (black's back)
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = WHITE
        self.en_passant_target = None  # (col, row) of pawn that can be captured en passant
        self.move_history = []

    def setup_initial_position(self):
        """Set up the starting position with pawns on rows 2 and 7"""
        # White pawns on row 2 (index 1)
        for col in range(BOARD_SIZE):
            self.board[1][col] = WHITE
        # Black pawns on row 7 (index 6)
        for col in range(BOARD_SIZE):
            self.board[6][col] = BLACK

    def setup_from_string(self, setup_str):
        """Parse setup string like 'Setup Wb4 Wa3 Wc2 Bg7 Wd4 Bg6 Be7'"""
        # Clear board first
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        parts = setup_str.split()
        if parts[0] == "Setup":
            parts = parts[1:]

        for piece in parts:
            if len(piece) >= 3:
                color = piece[0]  # W or B
                col = ord(piece[1]) - ord('a')  # a-h -> 0-7
                row = int(piece[2]) - 1  # 1-8 -> 0-7
                if 0 <= col < 8 and 0 <= row < 8:
                    self.board[row][col] = color

    def copy(self):
        """Create a deep copy of the game state"""
        new_state = GameState()
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.en_passant_target = self.en_passant_target
        new_state.move_history = self.move_history[:]
        return new_state

    def get_piece(self, col, row):
        """Get piece at position, return EMPTY if out of bounds"""
        if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
            return self.board[row][col]
        return None

    def is_valid_pos(self, col, row):
        return 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE

    def get_all_pieces(self, color):
        """Get list of (col, row) for all pieces of given color"""
        pieces = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == color:
                    pieces.append((col, row))
        return pieces

    def generate_moves(self):
        """Generate all legal moves for current player"""
        moves = []
        player = self.current_player
        direction = 1 if player == WHITE else -1  # White moves up (increasing row), Black moves down
        start_row = 1 if player == WHITE else 6

        pieces = self.get_all_pieces(player)
        opponent = BLACK if player == WHITE else WHITE

        for col, row in pieces:
            # Move forward one square
            new_row = row + direction
            if self.is_valid_pos(col, new_row) and self.board[new_row][col] == EMPTY:
                moves.append((col, row, col, new_row))

                # Double move from starting position
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if self.is_valid_pos(col, new_row2) and self.board[new_row2][col] == EMPTY:
                        moves.append((col, row, col, new_row2))

            # Captures (diagonal)
            for dcol in [-1, 1]:
                new_col = col + dcol
                new_row = row + direction
                if self.is_valid_pos(new_col, new_row):
                    target = self.board[new_row][new_col]
                    if target == opponent:
                        moves.append((col, row, new_col, new_row))
                    # En passant
                    elif self.en_passant_target and (new_col, new_row) == self.en_passant_target:
                        # Check if there's an enemy pawn next to us that just moved
                        if self.board[row][new_col] == opponent:
                            moves.append((col, row, new_col, new_row))

        return moves

    def make_move(self, move):
        """Make a move and return new game state"""
        from_col, from_row, to_col, to_row = move
        new_state = self.copy()

        piece = new_state.board[from_row][from_col]

        # Check for en passant capture
        if new_state.en_passant_target and (to_col, to_row) == new_state.en_passant_target:
            # Remove the captured pawn (it's on the same row as the capturing pawn)
            captured_row = from_row
            new_state.board[captured_row][to_col] = EMPTY

        # Move the piece
        new_state.board[from_row][from_col] = EMPTY
        new_state.board[to_row][to_col] = piece

        # Set en passant target if double move
        new_state.en_passant_target = None
        if abs(to_row - from_row) == 2:
            # En passant target is the square behind the pawn
            ep_row = (from_row + to_row) // 2
            new_state.en_passant_target = (to_col, ep_row)

        # Switch player
        new_state.current_player = BLACK if new_state.current_player == WHITE else WHITE
        new_state.move_history.append(move)

        return new_state

    def is_terminal(self):
        """Check if game is over, return (is_over, winner)"""
        # Check if a pawn reached the end
        for col in range(BOARD_SIZE):
            if self.board[7][col] == WHITE:
                return True, WHITE
            if self.board[0][col] == BLACK:
                return True, BLACK

        # Check if one side has no pawns
        white_pawns = len(self.get_all_pieces(WHITE))
        black_pawns = len(self.get_all_pieces(BLACK))

        if white_pawns == 0:
            return True, BLACK
        if black_pawns == 0:
            return True, WHITE

        # Check if current player has no moves
        moves = self.generate_moves()
        if len(moves) == 0:
            # Current player loses
            winner = BLACK if self.current_player == WHITE else WHITE
            return True, winner

        return False, None

    def move_to_string(self, move):
        """Convert move tuple to string like 'e2e4'"""
        from_col, from_row, to_col, to_row = move
        return chr(ord('a') + from_col) + str(from_row + 1) + chr(ord('a') + to_col) + str(to_row + 1)

    def string_to_move(self, move_str):
        """Convert string like 'e2e4' to move tuple"""
        if len(move_str) < 4:
            return None
        from_col = ord(move_str[0]) - ord('a')
        from_row = int(move_str[1]) - 1
        to_col = ord(move_str[2]) - ord('a')
        to_row = int(move_str[3]) - 1
        return (from_col, from_row, to_col, to_row)

    def print_board(self):
        """Print the board for debugging"""
        print("  a b c d e f g h")
        for row in range(BOARD_SIZE - 1, -1, -1):
            print(f"{row + 1} ", end="")
            for col in range(BOARD_SIZE):
                print(self.board[row][col] + " ", end="")
            print(f"{row + 1}")
        print("  a b c d e f g h")


class Evaluator:
    """Evaluation function for the Two Flags game"""

    def __init__(self):
        # How much we value advancement (closer to promotion = better)
        self.advancement_weight = 10
        # How much we value having more pawns
        self.material_weight = 100
        # How much we value passed pawns (no enemy pawn blocking)
        self.passed_pawn_weight = 30
        # Center control bonus
        self.center_weight = 5

    def evaluate(self, state, maximizing_color):
        """
        Evaluate the position from the perspective of maximizing_color
        Positive = good for maximizing_color, Negative = bad
        """
        # Check terminal state first
        is_over, winner = state.is_terminal()
        if is_over:
            if winner == maximizing_color:
                return WIN_VALUE
            elif winner is not None:
                return -WIN_VALUE
            else:
                return 0  # draw somehow?

        score = 0
        opponent = BLACK if maximizing_color == WHITE else WHITE

        my_pawns = state.get_all_pieces(maximizing_color)
        opp_pawns = state.get_all_pieces(opponent)

        # Material count
        score += (len(my_pawns) - len(opp_pawns)) * self.material_weight

        # Advancement score
        for col, row in my_pawns:
            if maximizing_color == WHITE:
                advancement = row  # Higher row = closer to promotion for white
            else:
                advancement = 7 - row  # Lower row = closer to promotion for black
            score += advancement * self.advancement_weight

            # Bonus for passed pawns
            if self.is_passed_pawn(state, col, row, maximizing_color):
                score += self.passed_pawn_weight + (advancement * 5)

            # Center control bonus (columns c-f)
            if 2 <= col <= 5:
                score += self.center_weight

        # Penalize opponent advancement
        for col, row in opp_pawns:
            if opponent == WHITE:
                advancement = row
            else:
                advancement = 7 - row
            score -= advancement * self.advancement_weight

            if self.is_passed_pawn(state, col, row, opponent):
                score -= self.passed_pawn_weight + (advancement * 5)

        return score

    def is_passed_pawn(self, state, col, row, color):
        """Check if a pawn has no enemy pawns blocking its path"""
        opponent = BLACK if color == WHITE else WHITE
        direction = 1 if color == WHITE else -1

        # Check the column and adjacent columns ahead
        check_row = row + direction
        while 0 <= check_row < 8:
            for check_col in [col - 1, col, col + 1]:
                if 0 <= check_col < 8:
                    if state.board[check_row][check_col] == opponent:
                        return False
            check_row += direction
        return True


class TwoFlagsAI:
    """AI Player using Minimax with Alpha-Beta pruning"""

    def __init__(self, color, time_limit_minutes=30):
        self.color = color
        self.evaluator = Evaluator()
        self.time_limit = time_limit_minutes * 60  # convert to seconds
        self.time_used = 0
        self.start_time = None
        self.nodes_searched = 0
        self.max_depth_reached = 0

    def get_time_for_move(self):
        """Calculate how much time to spend on this move"""
        remaining = self.time_limit - self.time_used
        # Simple time management: use about 1/30 of remaining time per move
        # but at least 0.5 seconds and at most 10 seconds
        time_for_move = remaining / 30
        time_for_move = max(0.5, min(time_for_move, 10))
        return time_for_move

    def should_stop(self):
        """Check if we should stop searching"""
        if self.start_time is None:
            return False
        elapsed = time.time() - self.start_time
        return elapsed >= self.move_time_limit

    def get_best_move(self, state):
        """Get the best move for the current position using iterative deepening"""
        self.start_time = time.time()
        self.move_time_limit = self.get_time_for_move()
        self.nodes_searched = 0

        moves = state.generate_moves()
        if not moves:
            return None

        if len(moves) == 1:
            return moves[0]

        best_move = moves[0]  # default to first move

        # Iterative deepening
        for depth in range(1, 50):
            if self.should_stop():
                break

            try:
                move, score = self.search_root(state, depth)
                if move is not None:
                    best_move = move
                    self.max_depth_reached = depth

                # If we found a winning move, stop searching
                if score >= WIN_VALUE - 100:
                    break

            except TimeoutError:
                break

        elapsed = time.time() - self.start_time
        self.time_used += elapsed

        return best_move

    def search_root(self, state, depth):
        """Search from root position"""
        moves = state.generate_moves()
        if not moves:
            return None, -WIN_VALUE

        # Move ordering: try captures first, then center moves
        moves = self.order_moves(state, moves)

        best_move = moves[0]
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in moves:
            if self.should_stop():
                raise TimeoutError()

            new_state = state.make_move(move)
            score = -self.alpha_beta(new_state, depth - 1, -beta, -alpha, False)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move, best_score

    def alpha_beta(self, state, depth, alpha, beta, maximizing):
        """Alpha-beta search"""
        self.nodes_searched += 1

        if self.should_stop():
            raise TimeoutError()

        # Check terminal
        is_over, winner = state.is_terminal()
        if is_over:
            if winner == self.color:
                return WIN_VALUE - (50 - depth)  # prefer faster wins
            elif winner is not None:
                return -WIN_VALUE + (50 - depth)  # avoid faster losses
            return 0

        if depth <= 0:
            return self.evaluator.evaluate(state, self.color)

        moves = state.generate_moves()
        moves = self.order_moves(state, moves)

        best_score = float('-inf')

        for move in moves:
            new_state = state.make_move(move)
            score = -self.alpha_beta(new_state, depth - 1, -beta, -alpha, not maximizing)

            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if alpha >= beta:
                break  # beta cutoff

        return best_score

    def order_moves(self, state, moves):
        """Order moves for better alpha-beta pruning"""
        scored_moves = []
        opponent = BLACK if state.current_player == WHITE else WHITE

        for move in moves:
            score = 0
            from_col, from_row, to_col, to_row = move

            # Captures are good
            if state.board[to_row][to_col] == opponent:
                score += 100

            # En passant captures
            if state.en_passant_target and (to_col, to_row) == state.en_passant_target:
                score += 100

            # Advancement is good
            if state.current_player == WHITE:
                score += to_row * 5
            else:
                score += (7 - to_row) * 5

            # Center moves
            if 2 <= to_col <= 5:
                score += 3

            scored_moves.append((score, move))

        # Sort by score descending
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [move for score, move in scored_moves]

    def set_time_limit(self, minutes):
        """Set total time limit for the game"""
        self.time_limit = minutes * 60
        self.time_used = 0


def play_human_vs_ai():
    """Play a game against the AI"""
    state = GameState()
    state.setup_initial_position()

    print("Two Flags Game - Human vs AI")
    print("You play White, AI plays Black")
    print("Enter moves in format: e2e4")
    print("Type 'quit' to exit\n")

    ai = TwoFlagsAI(BLACK, 30)

    while True:
        state.print_board()
        is_over, winner = state.is_terminal()
        if is_over:
            if winner == WHITE:
                print("You win!")
            elif winner == BLACK:
                print("AI wins!")
            else:
                print("Draw!")
            break

        if state.current_player == WHITE:
            # Human move
            moves = state.generate_moves()
            print(f"\nYour turn (White). Legal moves: {[state.move_to_string(m) for m in moves]}")

            while True:
                move_str = input("Enter your move: ").strip().lower()
                if move_str == 'quit':
                    print("Thanks for playing!")
                    return

                move = state.string_to_move(move_str)
                if move and move in moves:
                    state = state.make_move(move)
                    break
                else:
                    print("Invalid move, try again")
        else:
            # AI move
            print("\nAI is thinking...")
            move = ai.get_best_move(state)
            if move:
                print(f"AI plays: {state.move_to_string(move)}")
                state = state.make_move(move)
            else:
                print("AI has no moves!")
                break


def play_ai_vs_ai():
    """Watch two AIs play against each other"""
    state = GameState()
    state.setup_initial_position()

    print("Two Flags Game - AI vs AI")

    white_ai = TwoFlagsAI(WHITE, 5)
    black_ai = TwoFlagsAI(BLACK, 5)

    move_count = 0
    while True:
        state.print_board()
        print()

        is_over, winner = state.is_terminal()
        if is_over:
            if winner == WHITE:
                print("White wins!")
            elif winner == BLACK:
                print("Black wins!")
            else:
                print("Draw!")
            break

        if move_count > 200:
            print("Game too long, ending...")
            break

        if state.current_player == WHITE:
            ai = white_ai
        else:
            ai = black_ai

        print(f"{state.current_player}'s turn...")
        move = ai.get_best_move(state)

        if move:
            print(f"Move: {state.move_to_string(move)} (searched {ai.nodes_searched} nodes, depth {ai.max_depth_reached})")
            state = state.make_move(move)
            move_count += 1
        else:
            print(f"{state.current_player} has no moves!")
            break

        time.sleep(0.5)  # small delay so we can see the game


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "aivsai":
        play_ai_vs_ai()
    else:
        play_human_vs_ai()
