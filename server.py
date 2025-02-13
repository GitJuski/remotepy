import socket
import argparse
import subprocess
import ssl

# Command line arguments
parser = argparse.ArgumentParser(prog="serverpy", description="Remote connection server")
parser.add_argument("-l", "--listen", required=False, help="Example usage: -l 127.0.0.1")
parser.add_argument("-p", "--port", required=True, help="Example usage: -p 4444")
args = parser.parse_args()

# Listen address and port. Defaults to 0.0.0.0
LISTEN: str = args.listen
PORT: int = int(args.port)

if LISTEN == None:
    LISTEN = "0.0.0.0"

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # Use TLS
context.load_cert_chain("server-cert.pem", "server-key.pem") # Use this cert and key

try:
    # Start listening for connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LISTEN, PORT))
        s.listen()
        print(f"Listening on {PORT}")

        # Wrap the socket with TLS
        with context.wrap_socket(s, server_side=True) as ssock:
            conn, addr = ssock.accept() # Accept the connection encrypted
            with conn:
                print(f"Connected by {addr}")
                while True:
                    command = conn.recv(1024).decode() # Receive a command from the client
                    if not command:
                        break
                    else:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True) # Run the command locally
                        if not result.stderr: # If it does not result in a error -> send result
                            conn.sendall((result.stdout).encode())
                        else: # If it results in error -> send error
                            conn.sendall((result.stderr).encode())

except KeyboardInterrupt:
    print("Exiting...\n")
except Exception as e:
    print(e)
