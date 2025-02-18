import socket
import argparse
import ssl

# Command line arguments
parser = argparse.ArgumentParser(prog="clientpy", description="A remote connection client")
parser.add_argument("--host", required=True, help="Example usage: --host 127.0.0.1")
parser.add_argument("-p", "--port", required=True, help="Example usage: -p 4444")
args = parser.parse_args()

# Host address and port
HOST: str = args.host
PORT: int = int(args.port)
ANSI_GREEN: str = "\x1b[32m"
ANSI_RED: str = "\x1b[31m"
ANSI_RESET: str = "\x1b[0m"

# ssl module context settings. The last two are to allow self signed certificate.
context = ssl.create_default_context()
context.check_hostname = False # Unsafe, but needed for self signed to work
context.verify_mode = ssl.CERT_NONE # Unsafe, but needed for self signed to work

try:
    # Initialize socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap socket
        with context.wrap_socket(s, server_hostname=HOST) as ssock:
            # Connect with wrapped socket
            ssock.connect((HOST, PORT))
            path: str = ssock.recv(1024).decode() # Receive the current working directory
            while True:
                command: str = input(f"{ANSI_GREEN}{path}${ANSI_RESET} ")
                if command == "exit":
                    break
                ssock.sendall((command).encode()) # Send the command to the server
                if not command.startswith("cd"):
                    data = ssock.recv(4096).decode() # Receive the response data
                    print(data)
                elif command.startswith("cd"): # If the command starts with cd ...
                    path = ssock.recv(1024).decode() # Receive the new current working directory

except KeyboardInterrupt:
    print(f"{ANSI_RED}Exiting...{ANSI_RESET}\n")
except Exception as e:
    print(e)
