# A program that has both server and client.
import socket
import subprocess
import os
import argparse
import ssl
import sys

def serverHandler(listen: int) -> None:
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # Use TLS
    context.load_cert_chain("server-cert.pem", "server-key.pem") # Use this cert and key

    try:
        # Start listening for connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", listen))
            s.listen()
            print(f"Listening on {listen}")

            # Wrap the socket with TLS
            with context.wrap_socket(s, server_side=True) as ssock:
                conn, addr = ssock.accept() # Accept the connection encrypted
                with conn:
                    print(f"Connected by {addr}")
                    conn.sendall(os.getcwd().encode()) # Send the current working directory
                    while True:
                        command = conn.recv(1024).decode() # Receive a command from the client
                        if not command:
                            break
                        if command.startswith("cd"):
                            try:
                                # Split the command so cd .. would return ["cd", ".."]. Change into the second part eg. "..". Send the current working directory after move
                                command = command.split(" ")
                                os.chdir(command[-1])
                                conn.sendall(os.getcwd().encode())
                            except Exception as e:
                                print(e)
                        else:
                            result = subprocess.run(command, shell=True, capture_output=True, text=True) # Run the command locally
                            if not result.stdout:
                                conn.sendall("Nothing to show".encode())
                            if not result.stderr: # If it does not result in a error -> send result
                                conn.sendall((result.stdout).encode())
                            else: # If it results in error -> send error
                                conn.sendall((result.stderr).encode())

    except KeyboardInterrupt:
        print("Exiting...\n")
    except Exception as e:
        print(e)


def clientHandler(host: str, port: int) -> None:
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
            with context.wrap_socket(s, server_hostname=host) as ssock:
                # Connect with wrapped socket
                ssock.connect((host, port))
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
    

def main() -> None:
    # Command line arguments
    parser = argparse.ArgumentParser(prog="SnakeCat", description="Remote client and server")
    parser.add_argument("-l", "--listen", required=False, help="Listening port. The application uses the server mode eg. -l 4444")
    parser.add_argument("-p", "--port", required=False, help="Target port eg. 4444")
    parser.add_argument("--host", required=False, help="Target host IP address eg. 127.0.0.1")
    args = parser.parse_args()

    listen: str = args.listen
    port: str = args.port
    host: str = args.host

    # If all command line arguments are None
    if not listen and not port and not host:
        print("Use the flag -l to start a server listener. Use --host and -p to connect to a host. Check help with -h or --help")
        sys.exit()
        

    # If listen argument is None
    if not listen:
        try:
            clientHandler(host, int(port))
        except TypeError:
            print("Use the flag -l to start a server listener. Use --host and -p to connecto to a host. Check help with -h or --help")
            sys.exit()
    else:
        serverHandler(int(listen))

if __name__ == "__main__":
    main()
