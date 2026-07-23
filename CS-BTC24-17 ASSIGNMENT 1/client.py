import socket
import time
import sys
import os
import csv

# --- UPDATE THESE VALUES ---
ROLL_NO = "CS-BTC24-17"
NAME = "SUPRATIM GOGOI"
# Timeout Rule based on last digit of roll number[cite: 1]:
# 0-1 (0.5s), 2-3 (0.7s), 4-5 (1.0s), 6-7 (1.2s), 8-9 (1.5s)[cite: 1]
TIMEOUT_VAL = 1.2  # Change this to match your roll number![cite: 1]
# ---------------------------

UDP_IP = "10.0.0.1"  # Server IP (h1)[cite: 1]
UDP_PORT = 5005
TOTAL_MESSAGES = 10  #[cite: 1]

# Accept loss percentage from command line arguments
loss_percent = sys.argv[1] if len(sys.argv) > 1 else "0"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT_VAL)  # Stop-and-Wait timeout mechanism[cite: 1]

total_packets_sent = 0
total_retransmissions = 0
status = "SUCCESS" #[cite: 1]

print(f"Client starting transfer. Sending {TOTAL_MESSAGES} messages...")

start_time = time.time()

for seq in range(1, TOTAL_MESSAGES + 1):
    message = f"{seq} Message {seq} from h2"  #[cite: 1]
    ack_received = False
    
    while not ack_received:
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        total_packets_sent += 1
        
        try:
            # Wait for ACK[cite: 1]
            data, addr = sock.recvfrom(1024)
            ack_msg = data.decode()
            
            if ack_msg == f"ACK {seq}":  # Correct ACK format[cite: 1]
                ack_received = True
                
        except socket.timeout:
            # Retransmit if ACK is not received before timeout[cite: 1]
            total_retransmissions += 1

end_time = time.time()
transfer_time = round(end_time - start_time, 4)

# Required Client Output[cite: 1]
print(f"\nTOTAL_MESSAGES = {TOTAL_MESSAGES}") #[cite: 1]
print(f"LOSS_PERCENT={loss_percent}") #[cite: 1]
print(f"TIMEOUT={TIMEOUT_VAL}") #[cite: 1]
print(f"TOTAL_PACKETS_SENT={total_packets_sent}") #[cite: 1]
print(f"TOTAL_RETRANSMISSIONS={total_retransmissions}") #[cite: 1]
print(f"TRANSFER_TIME_SECONDS={transfer_time}") #[cite: 1]
print(f"STATUS {status}") #[cite: 1]

# --- AUTOMATIC CSV CREATION ---
csv_filename = "result_table.csv"
file_exists = os.path.isfile(csv_filename)

# Write the data to the CSV file
with open(csv_filename, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # Write the exact headers requested if the file is being created for the first time[cite: 1]
    if not file_exists:
        writer.writerow(["roll_no", "name", "loss_percent", "timeout", "total_messages", 
                         "total_packets_sent", "total_retransmissions", "transfer_time_seconds", "status"]) #[cite: 1]
        
    # Append the results of this specific run
    writer.writerow([ROLL_NO, NAME, loss_percent, TIMEOUT_VAL, TOTAL_MESSAGES, 
                     total_packets_sent, total_retransmissions, transfer_time, status])

print(f"\nResults automatically saved to {csv_filename}!")