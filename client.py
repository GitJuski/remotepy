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
            while True:
                command: str = input("")
                if command == "exit":
                    break
                ssock.sendall((command).encode()) # Send the command to the server
                data = ssock.recv(1024).decode() # Receive the response data
                print(data)

except KeyboardInterrupt:
    print("Exiting...\n")
except Exception as e:
    print(e)
