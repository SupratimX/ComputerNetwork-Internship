import socket

# Configuration
UDP_IP = "10.0.0.1"  # Default h1 IP
UDP_PORT = 5005
EXPECTED_MESSAGES = 10  #

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

received_seqs = set()
duplicates_detected = 0

print(f"Server listening on {UDP_IP}:{UDP_PORT}")

# Run until 10 unique messages are received
while len(received_seqs) < EXPECTED_MESSAGES:
    data, addr = sock.recvfrom(1024)
    message = data.decode()
    
    # Parse the SEQ number from the message format "SEQ MESSAGE"
    try:
        seq_str, rest = message.split(" ", 1)
        seq = int(seq_str)
    except ValueError:
        continue

    # Detect duplicates
    if seq in received_seqs:
        duplicates_detected += 1
    else:
        received_seqs.add(seq)
        
    # Send ACK back to the client
    ack_message = f"ACK {seq}"  #
    sock.sendto(ack_message.encode(), addr)

# Required Server Output
print(f"\nTOTAL_UNIQUE_MESSAGES_RECEIVED = {len(received_seqs)}") #
print(f"TOTAL_DUPLICATES_DETECTED={duplicates_detected}") #
print("STATUS SUCCESS") #