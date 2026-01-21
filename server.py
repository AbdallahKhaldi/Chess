#!/usr/bin/env python3
"""
Simple test server for Two Flags Game
Used to test the client locally before tournament
"""

import socket
import sys
from two_flags import GameState, WHITE, BLACK


def main():
    if len(sys.argv) < 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', port))
    server_sock.listen(1)

    print(f"Server listening on port {port}")
    print("Waiting for a client to connect...")

    client_sock, addr = server_sock.accept()
    print(f"Connected with client at {addr}")

    def send(msg):
        client_sock.sendall(msg.encode())
        print(f"Sent: {msg}")

    def receive():
        data = client_sock.recv(4096).decode().strip()
        print(f"Client: {data}")
        return data

    try:
        # Send connection message
        send("Connected to the server!")

        # Wait for OK
        msg = receive()

        # Send Setup
        send("Setup Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7")

        # Wait for OK
        msg = receive()

        # Send Time
        send("Time 30")

        # Wait for OK
        msg = receive()

        # Initialize game state
        state = GameState()
        state.setup_initial_position()

        print("\n--- Game Start ---")
        print("You control the server side. Enter moves or commands.")
        print("Enter 'begin' to let the client play White")
        print("Enter a move (e.g., 'e2e4') to play as White")
        print("Enter 'exit' to quit\n")

        state.print_board()

        while True:
            user_input = input("> ").strip()

            if user_input.lower() == 'exit':
                send("exit")
                break

            if user_input.lower() == 'begin':
                # Client plays White
                send("Begin")
                # Wait for client's move
                move_str = receive()
                if move_str.lower() == 'exit':
                    print("Client resigned")
                    break
                # Apply move
                move = state.string_to_move(move_str)
                if move:
                    state = state.make_move(move)
                    state.print_board()
                continue

            # Server plays as White, client plays as Black
            if len(user_input) == 4:
                # Send move to client
                send(user_input)
                # Apply to our state
                move = state.string_to_move(user_input)
                if move:
                    state = state.make_move(move)
                    state.print_board()

                # Wait for client response
                response = receive()
                if response.lower() == 'exit':
                    print("Client resigned")
                    break
                # Apply client's move
                move = state.string_to_move(response)
                if move:
                    state = state.make_move(move)
                    state.print_board()

                # Check game over
                is_over, winner = state.is_terminal()
                if is_over:
                    print(f"Game over! Winner: {winner}")
                    send("exit")
                    break

    except Exception as e:
        print(f"Error: {e}")

    client_sock.close()
    server_sock.close()
    print("Server closed")


if __name__ == "__main__":
    main()
