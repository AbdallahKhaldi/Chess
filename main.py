#!/usr/bin/env python3
"""
Two Flags Game - Main Entry Point
Run this file to play the game in different modes

Usage:
    python main.py              - Play against AI (you are White)
    python main.py aivsai       - Watch AI vs AI
    python main.py setup "..."  - Start from a custom position
    python main.py client HOST PORT - Connect to tournament server
"""

import sys
from two_flags import GameState, TwoFlagsAI, WHITE, BLACK, play_human_vs_ai, play_ai_vs_ai


def play_from_setup(setup_string):
    """Play from a custom starting position"""
    state = GameState()
    state.setup_from_string(setup_string)

    print("Two Flags Game - Custom Position")
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
            moves = state.generate_moves()
            print(f"\nYour turn. Legal moves: {[state.move_to_string(m) for m in moves]}")

            while True:
                move_str = input("Enter your move: ").strip().lower()
                if move_str == 'quit':
                    return

                move = state.string_to_move(move_str)
                if move and move in moves:
                    state = state.make_move(move)
                    break
                else:
                    print("Invalid move!")
        else:
            print("\nAI thinking...")
            move = ai.get_best_move(state)
            if move:
                print(f"AI plays: {state.move_to_string(move)}")
                state = state.make_move(move)


def show_help():
    print("""
Two Flags Game - AI Agent
=========================

A pawn-only chess variant where the goal is to reach the opposite side first.

Game Rules:
- Played on 8x8 board
- Each side has 8 pawns
- Pawns move like in chess (forward 1, capture diagonal, double move from start, en passant)
- Win by: reaching the last row, capturing all enemy pawns, or opponent has no moves

How to run:
-----------
python main.py              - Play against AI (you are White)
python main.py aivsai       - Watch AI vs AI game
python main.py setup "Setup Wb4 Wa3 Wc2 Bg7"  - Start from position
python main.py client 127.0.0.1 9999 - Connect to tournament server

Move format: e2e4 (source square + destination square)
""")


def main():
    if len(sys.argv) < 2:
        play_human_vs_ai()
        return

    mode = sys.argv[1].lower()

    if mode == "help" or mode == "-h" or mode == "--help":
        show_help()

    elif mode == "aivsai":
        play_ai_vs_ai()

    elif mode == "setup":
        if len(sys.argv) >= 3:
            setup_str = " ".join(sys.argv[2:])
            play_from_setup(setup_str)
        else:
            print("Please provide setup string, e.g.:")
            print('python main.py setup "Setup Wb4 Wa3 Wc2 Bg7"')

    elif mode == "client":
        if len(sys.argv) >= 4:
            from client import TwoFlagsClient
            host = sys.argv[2]
            port = int(sys.argv[3])
            client = TwoFlagsClient(host, port)
            client.run()
        else:
            print("Usage: python main.py client <host> <port>")

    else:
        print(f"Unknown mode: {mode}")
        show_help()


if __name__ == "__main__":
    main()
