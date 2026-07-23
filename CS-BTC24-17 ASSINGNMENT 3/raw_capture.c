#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netinet/udp.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define MAX_PACKETS 20
#define BUFFER_SIZE 65536

// UPDATE YOUR ROLL NUMBER AND ASSIGNED PROTOCOL HERE
#define ROLL_NO "2023CSB1001"
#define ASSIGNED_PROTOCOL "ICMP"

int main() {
    int raw_sock;
    unsigned char buffer[BUFFER_SIZE];
    struct sockaddr_in source, dest;
    int packet_count = 0;

    // Create raw socket listening for IP traffic
    raw_sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP); // Change to IPPROTO_UDP or IPPROTO_TCP if required
    if (raw_sock < 0) {
        perror("Socket Creation Error (Did you run with sudo?)");
        return 1;
    }

    printf("Starting Packet Capture...\n");
    printf("========================================\n");

    while (packet_count < MAX_PACKETS) {
        socklen_t saddr_len = sizeof(source);
        int data_size = recvfrom(raw_sock, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&source, &saddr_len);
        
        if (data_size < 0) {
            perror("Recvfrom Error");
            return 1;
        }

        // IP Header Parsing
        struct iphdr *iph = (struct iphdr *)buffer;
        
        // Task 5 Enhancement: IP Header Length & IP Version
        unsigned int iphlen = iph->ihl * 4;

        memset(&source, 0, sizeof(source));
        source.sin_addr.s_addr = iph->saddr;

        memset(&dest, 0, sizeof(dest));
        dest.sin_addr.s_addr = iph->daddr;

        packet_count++;

        // Required Output Format (Task 1)
        printf("ROLL NO=%s\n", ROLL_NO);
        printf("ASSIGNED PROTOCOL=%s\n", ASSIGNED_PROTOCOL);
        printf("PACKET NO=%d\n", packet_count);
        printf("SRC IP=%s\n", inet_ntoa(source.sin_addr));
        printf("DST IP=%s\n", inet_ntoa(dest.sin_addr));
        printf("PROTOCOL=%s\n", ASSIGNED_PROTOCOL);
        printf("PROTOCOL NO=%d\n", iph->protocol);
        printf("TTL=%d\n", iph->ttl);
        printf("PACKET SIZE=%d\n", ntohs(iph->tot_len));

        // Task 5 Enhancement Field Output
        printf("IP VERSION=%d\n", iph->version);
        printf("HEADER LENGTH=%d bytes\n", iphlen);

        // Protocol Specific Fields (ICMP Example)
        if (iph->protocol == IPPROTO_ICMP) {
            struct icmphdr *icmph = (struct icmphdr *)(buffer + iphlen);
            printf("ICMP TYPE=%d\n", icmph->type);
            printf("ICMP CODE=%d\n", icmph->code);
        }
        /*
        // For UDP (Roll No 4-6):
        else if (iph->protocol == IPPROTO_UDP) {
            struct udphdr *udph = (struct udphdr *)(buffer + iphlen);
            printf("SRC PORT=%d\n", ntohs(udph->source));
            printf("DST PORT=%d\n", ntohs(udph->dest));
        }
        // For TCP (Roll No 7-9):
        else if (iph->protocol == IPPROTO_TCP) {
            struct tcphdr *tcph = (struct tcphdr *)(buffer + iphlen);
            printf("SRC PORT=%d\n", ntohs(tcph->source));
            printf("DST PORT=%d\n", ntohs(tcph->dest));
            printf("SYN=%d ACK=%d FIN=%d RST=%d\n", tcph->syn, tcph->ack, tcph->fin, tcph->rst);
        }
        */

        printf("----------------------------------------\n");
    }

    close(raw_sock);
    return 0;
}