#!/usr/bin/env python3
"""
TCP/IP Client for Two Flags Game Tournament
Connects to server and plays the game using our AI agent
"""

import socket
import sys
import time
from two_flags import GameState, TwoFlagsAI, WHITE, BLACK


class TwoFlagsClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.state = None
        self.ai = None
        self.my_color = None
        self.time_limit = 30  # default

    def connect(self):
        """Connect to the server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send(self, message):
        """Send message to server (without newline as specified)"""
        try:
            self.sock.sendall(message.encode())
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Send error: {e}")

    def receive(self):
        """Receive message from server"""
        try:
            data = self.sock.recv(4096).decode().strip()
            print(f"Received: {data}")
            return data
        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def handle_setup(self, setup_str):
        """Handle Setup command from server"""
        self.state = GameState()
        if "Setup" in setup_str:
            self.state.setup_from_string(setup_str)
        else:
            # Default starting position
            self.state.setup_initial_position()
        print("Board setup complete:")
        self.state.print_board()

    def handle_time(self, time_str):
        """Handle Time command - format: 'Time X' where X is minutes"""
        try:
            parts = time_str.split()
            if len(parts) >= 2:
                self.time_limit = int(parts[1])
            print(f"Time limit set to {self.time_limit} minutes")
        except:
            print(f"Could not parse time, using default {self.time_limit} minutes")

    def handle_opponent_move(self, move_str):
        """Apply opponent's move to the board"""
        move_str = move_str.strip()
        move = self.state.string_to_move(move_str)
        if move:
            # Check if move is valid
            legal_moves = self.state.generate_moves()
            if move in legal_moves:
                self.state = self.state.make_move(move)
                print(f"Opponent played: {move_str}")
                self.state.print_board()
            else:
                print(f"Warning: opponent move {move_str} seems invalid, applying anyway")
                self.state = self.state.make_move(move)
        else:
            print(f"Could not parse opponent move: {move_str}")

    def get_my_move(self):
        """Get AI's move"""
        move = self.ai.get_best_move(self.state)
        if move:
            self.state = self.state.make_move(move)
            move_str = self.state.move_to_string(move)
            print(f"My move: {move_str} (depth {self.ai.max_depth_reached}, nodes {self.ai.nodes_searched})")
            self.state.print_board()
            return move_str
        return None

    def run(self):
        """Main client loop"""
        if not self.connect():
            return

        # Wait for connection confirmation
        msg = self.receive()
        if not msg or "Connected" not in msg:
            print("Did not receive connection confirmation")
            return

        # Send OK
        self.send("OK")

        # Wait for Setup or Time command
        setup_done = False
        time_done = False
        game_started = False

        while True:
            msg = self.receive()
            if not msg:
                print("Connection lost")
                break

            msg = msg.strip()

            # Check for exit
            if msg.lower() == "exit":
                print("Server ended the session")
                break

            # Handle Setup command
            if msg.startswith("Setup"):
                self.handle_setup(msg)
                setup_done = True
                self.send("OK")
                continue

            # Handle Time command
            if msg.startswith("Time"):
                self.handle_time(msg)
                time_done = True
                # Initialize AI with time limit
                self.ai = TwoFlagsAI(BLACK, self.time_limit)  # default to black
                self.send("OK")
                continue

            # Handle Begin command - we play White
            if msg == "Begin":
                print("We play White!")
                self.my_color = WHITE
                self.ai = TwoFlagsAI(WHITE, self.time_limit)
                game_started = True

                if self.state is None:
                    self.state = GameState()
                    self.state.setup_initial_position()

                # Make first move
                my_move = self.get_my_move()
                if my_move:
                    self.send(my_move)
                else:
                    print("No moves available!")
                    self.send("exit")
                    break
                continue

            # If we get here with a 4-character string, it's probably a move
            if len(msg) == 4 and msg[0].isalpha():
                # This is opponent's move, we play Black
                if self.my_color is None:
                    self.my_color = BLACK
                    self.ai = TwoFlagsAI(BLACK, self.time_limit)

                if self.state is None:
                    self.state = GameState()
                    self.state.setup_initial_position()

                # Apply opponent's move
                self.handle_opponent_move(msg)

                # Check if game is over
                is_over, winner = self.state.is_terminal()
                if is_over:
                    print(f"Game over! Winner: {winner}")
                    break

                # Make our move
                my_move = self.get_my_move()
                if my_move:
                    self.send(my_move)
                else:
                    print("No moves available, resigning")
                    self.send("exit")
                    break

                # Check if game is over after our move
                is_over, winner = self.state.is_terminal()
                if is_over:
                    print(f"Game over! Winner: {winner}")
                    # Don't break, wait for server confirmation

        self.sock.close()
        print("Connection closed")


def main():
    if len(sys.argv) < 3:
        print("Usage: python client.py <host> <port>")
        print("Example: python client.py 127.0.0.1 9999")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = TwoFlagsClient(host, port)
    client.run()


if __name__ == "__main__":
    main()
