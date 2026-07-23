import socket
import time
import csv
import sys
import matplotlib.pyplot as plt

SERVER_IP = '10.0.0.1'
SERVER_PORT = 5000
BUFFER_SIZE = 16384  

# Experiment Configurations
MODES = ['persistent', 'new_connection']
MESSAGE_SIZES = [100, 1000, 10000]  # Sizes in bytes
NUM_MESSAGES = 10  # Number of iterations per test

def generate_payload(size):
    return 'X' * size

def generate_graphs(summary_results):
    print("\n[*] Generating graphs...")
    
    sizes_str = [str(s) for s in MESSAGE_SIZES]
    x_indexes = range(len(sizes_str))
    bar_width = 0.35

    # Extract data for plotting
    persistent_rtt = [row['Avg_Response_Time_ms'] for row in summary_results if row['Mode'] == 'persistent']
    new_conn_rtt = [row['Avg_Response_Time_ms'] for row in summary_results if row['Mode'] == 'new_connection']
    
    persistent_tput = [row['Throughput_Kbps'] for row in summary_results if row['Mode'] == 'persistent']
    new_conn_tput = [row['Throughput_Kbps'] for row in summary_results if row['Mode'] == 'new_connection']

    # --- Plot 1: Average Response Time ---
    plt.figure(figsize=(8, 5))
    plt.bar([x - bar_width/2 for x in x_indexes], persistent_rtt, width=bar_width, label='Persistent', color='#1f77b4')
    plt.bar([x + bar_width/2 for x in x_indexes], new_conn_rtt, width=bar_width, label='New Connection', color='#ff7f0e')
    
    plt.xlabel('Payload Size (Bytes)', fontweight='bold')
    plt.ylabel('Average Response Time (ms)', fontweight='bold')
    plt.title('TCP Response Time vs. Payload Size', fontweight='bold')
    plt.xticks(x_indexes, sizes_str)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('response_time_graph.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] Saved 'response_time_graph.png'")

    # --- Plot 2: Throughput ---
    plt.figure(figsize=(8, 5))
    plt.bar([x - bar_width/2 for x in x_indexes], persistent_tput, width=bar_width, label='Persistent', color='#2ca02c')
    plt.bar([x + bar_width/2 for x in x_indexes], new_conn_tput, width=bar_width, label='New Connection', color='#d62728')
    
    plt.xlabel('Payload Size (Bytes)', fontweight='bold')
    plt.ylabel('Throughput (Kbps)', fontweight='bold')
    plt.title('TCP Throughput vs. Payload Size', fontweight='bold')
    plt.xticks(x_indexes, sizes_str)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('throughput_graph.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("[+] Saved 'throughput_graph.png'")


def run_experiment():
    logs = []
    summary_results = []

    print("[*] Starting TCP Connection Performance Test...")

    for mode in MODES:
        for size in MESSAGE_SIZES:
            print(f"\n--- Testing Mode: {mode.upper()} | Payload Size: {size} Bytes ---")
            
            payload_data = generate_payload(size)
            rtts = []
            conn = None

            if mode == 'persistent':
                try:
                    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn.connect((SERVER_IP, SERVER_PORT))
                except Exception as e:
                    print(f"[-] Failed to establish persistent connection: {e}")
                    continue

            for msg_id in range(1, NUM_MESSAGES + 1):
                msg_str = f"MSG_ID:{msg_id}|SIZE:{size}|DATA:{payload_data}\n"
                
                start_time = time.time()

                if mode == 'new_connection':
                    try:
                        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        conn.connect((SERVER_IP, SERVER_PORT))
                    except Exception as e:
                        print(f"[-] Connection failed for MSG {msg_id}: {e}")
                        continue

                # Send Data
                conn.sendall(msg_str.encode('utf-8'))

                # Receive ACK
                response = conn.recv(BUFFER_SIZE).decode('utf-8')
                end_time = time.time()

                rtt = (end_time - start_time) * 1000  # ms
                rtts.append(rtt)

                if mode == 'new_connection':
                    conn.close()

                # Log detail
                logs.append({
                    'Mode': mode,
                    'Message_ID': msg_id,
                    'Size_Bytes': size,
                    'RTT_ms': round(rtt, 3),
                    'Response_Received': response.strip()
                })
                print(f"Msg {msg_id}/{NUM_MESSAGES} | RTT: {rtt:.3f} ms")

            if mode == 'persistent' and conn:
                conn.close()

            # Calculate aggregated metrics
            avg_rtt = sum(rtts) / len(rtts) if rtts else 0
            total_bytes = size * NUM_MESSAGES
            total_time_sec = sum(rtts) / 1000.0
            throughput_kbps = ((total_bytes * 8) / 1000) / total_time_sec if total_time_sec > 0 else 0

            summary_results.append({
                'Mode': mode,
                'Payload_Size_Bytes': size,
                'Total_Messages': NUM_MESSAGES,
                'Avg_Response_Time_ms': round(avg_rtt, 3),
                'Throughput_Kbps': round(throughput_kbps, 2)
            })

    # Save detailed log to message_responses_log.csv
    with open('message_responses_log.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Mode', 'Message_ID', 'Size_Bytes', 'RTT_ms', 'Response_Received'])
        writer.writeheader()
        writer.writerows(logs)
    print("\n[+] Saved detailed logs to 'message_responses_log.csv'")

    # Save summary table to result_table.csv
    with open('result_table.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Mode', 'Payload_Size_Bytes', 'Total_Messages', 'Avg_Response_Time_ms', 'Throughput_Kbps'])
        writer.writeheader()
        writer.writerows(summary_results)
    print("[+] Saved summary results to 'result_table.csv'")

    # Automatically generate the plots
    generate_graphs(summary_results)

if __name__ == "__main__":
    run_experiment()