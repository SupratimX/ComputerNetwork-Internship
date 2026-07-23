import socket
import sys

HOST = '10.0.0.1'  # Mininet h1 Server IP
PORT = 5000
BUFFER_SIZE = 16384

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[+] Server started on {HOST}:{PORT}. Waiting for connections...")
    except Exception as e:
        print(f"[-] Bind failed: {e}")
        sys.exit(1)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[+] Connection accepted from {client_address}")
            
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break  # Client closed connection
                
                message = data.decode('utf-8')
                print(f"[RECEIVED] Raw Data: {message.strip()}")
                
                # Parse message payload (Expected Format: "MSG_ID:<id>|SIZE:<size>|DATA:<payload>")
                try:
                    parts = message.strip().split('|')
                    msg_id = parts[0].split(':')[1]
                    msg_size = parts[1].split(':')[1]
                    
                    response = f"ACK|MSG_ID:{msg_id}|SIZE:{msg_size}\n"
                    client_socket.sendall(response.encode('utf-8'))
                    print(f"[SENT] {response.strip()}")
                except Exception as parse_error:
                    error_resp = "ERR|INVALID_FORMAT\n"
                    client_socket.sendall(error_resp.encode('utf-8'))
                    print(f"[-] Parsing error: {parse_error}")

            client_socket.close()
            print(f"[-] Connection closed with {client_address}")
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down server gracefully...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()