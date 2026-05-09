# Packet Analyzer Platform

A professional-grade packet capture and analysis platform with real-time packet visualization, filtering, statistics, and advanced algorithm comparison capabilities. Similar to Wireshark but with a web-based interface. documantation is left in case of exploring problems and errors and how were they solved ^^

**please be aware that this project may not be 100% accurate, and it may get some bugs in the capture process**

## Features

### Core Capture Features
- **Real-time Packet Capture**: Continuous packet capture until user stops (no packet limit)
- **Live Statistics**: Real-time display of captured packet count and per-protocol statistics
- **Protocol Support**: TCP, UDP, ARP, ICMP, HTTP, HTTPS (TLS)
- **Packet Details**: View number, source, destination, and detailed packet information
- **Cross-Platform**: both tested and verified working on the big three

### Analysis & Filtering
- **Protocol Filtering**: Filter packets by protocol (TCP, UDP, ARP, ICMP, HTTP/HTTPS)
- **Advanced Search**: Filter by source IP, destination IP, port numbers
- **Real-time Pie Chart**: Visual distribution of captured packets by protocol, source, or destination
- **Dynamic Statistics**: Real-time statistics including most common protocols, sources, and destinations

### File Management
- **Save Captures**: Export captured packets to PCAP files in the "captures" directory
- **Load PCAP Files**: Analyze previously captured PCAP files
- **Statistics Export**: Save and load packet statistics for later analysis

### Advanced Features
- **Ruleset System**: Compare pattern matching algorithms (Quick Search, Boyer-Moore, KMP)
  - Automatically selects a random packet as a ruleset after 1000+ packets captured
  - Compares algorithm performance and execution time on payload data
  - **Sequential Mode**: Algorithms run one after another (baseline performance)
  - **Parallel Mode**: All algorithms run simultaneously (demonstrates parallelization speedup)
  - Pattern matching searches application layer payloads only (realistic data)
  - Apply rulesets as filters or save for later use
- **Filter Management**: Apply, clear, and manage packet filters in real-time
- **Session Management**: Clear captured packets and start fresh analysis
- **Execution Modes**: Toggle between sequential and parallel algorithm execution for performance comparison

## Quick Start

### Windows
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run application
python app.py

# Open browser to http://localhost:5000
```

### Linux/macOS
```bash
# Activate virtual environment
source venv/bin/activate

# Run application
python app.py

# Open browser to http://localhost:5000
```

For detailed setup instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

## Platform Requirements

- **Python 3.8+**
- **Administrator/sudo privileges** (packet capture requires elevated permissions)
- Modern web browser (Chrome, Firefox, Edge, Safari)
- **Windows**: npcap driver 
- **Linux**: libpcap development files
- **macOS**: System tools available by default

## Troubleshooting

For common issues and their solutions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

If you encounter problems:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for your issue
2. Ensure npcap (Windows) or libpcap (Linux) is installed
3. Run with administrator/sudo privileges
4. Check that port 5000 is not in use

## Ruleset Experiment Modes

The ruleset system supports two execution modes for algorithm comparison:

### Sequential Mode (Default)
- Algorithms run one after another
- Total time = Quick Search time + Boyer-Moore time + KMP time
- Baseline for performance comparison
- Useful for understanding individual algorithm performance

### Parallel Mode
- All three algorithms run simultaneously using threading
- Total time ≈ slowest algorithm's time (typically 2-3x faster than sequential)
- Demonstrates parallelization benefits
- Best for high-volume packet analysis

## classifications
you may encounter some minor differences in the way packets are classified. 
- general classification is clear and consistent with the protocol types. backend' endpoint iterates through all packets and groups them by protocol type (TCP, UDP, ARP, ICMP, HTTP/HTTPS).
- however, pie chart classification is more specific, it may split some tcp packets for example into other categories "IP" or "IPv6", these packets have the IP/IPv6 layer but not the transport layer detected. this happens when:-
  * packet has an IP header but no TCP/UDP/ICMP layers
  * raw protocol packet
  * fragmented packets (missing upper layers)
  * tunnel/ encapsulated packets 
  * incomplete packet captures
- but the seperation actually does happen like this:-
### for tcp:-
  * HTTPS: port 443 and payload starts with 0x16 (TLS handshake) or 0x17 (TLS application data)
  * HTTP: port 80 and payload starts with GET, POST
  * TCP: port 80/443 but no valid HTTP/HTTPS payload, or other TCP traffic
### for udp:-
UDP seperation is simpler, its just port-based:
  * DNS: port 53 detected 
  * UDP: other UDP traffic (53, 5353, etc)
### other protocols:-
ICMP, ICMPv6, ARP, IP, IPv6 and ethernet are always classified as is, they are not split into subcategories. if a packet has an IP header but no transport layer, it will be classified as "IP" or "IPv6" in the pie chart, but still counted as TCP/UDP in the main stats. this is because the main stats classify by highest detected layer, while the pie chart classifies by specific protocol signatures. this can lead to some packets being counted in multiple categories, but it reflects the reality of packet structures and capture limitations.
