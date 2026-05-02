# Packet Analyzer Platform

A professional-grade packet capture and analysis platform with real-time packet visualization, filtering, statistics, and advanced algorithm comparison capabilities. Similar to Wireshark but with a web-based interface.

## Features

### Core Capture Features
- **Real-time Packet Capture**: Continuous packet capture until user stops (no packet limit)
- **Live Statistics**: Real-time display of captured packet count and per-protocol statistics
- **Protocol Support**: TCP, UDP, ARP, ICMP, HTTP, HTTPS (TLS)
- **Packet Details**: View number, source, destination, and detailed packet information
- **Cross-Platform**: Windows, Linux, and macOS support

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
- **Ruleset System**: Compare pattern matching algorithms (Quick Search, Boyer-Moore, Aho-Corasick)
  - Automatically selects a random packet as a ruleset after 1000+ packets captured
  - Compares algorithm performance and execution time
  - Apply rulesets as filters or save for later use
- **Filter Management**: Apply, clear, and manage packet filters in real-time
- **Session Management**: Clear captured packets and start fresh analysis

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
- **Windows**: npcap driver (see [NPCAP_SETUP.md](NPCAP_SETUP.md))
- **Linux**: libpcap development files
- **macOS**: System tools available by default

## Documentation

- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Platform-specific setup and running instructions
- [NPCAP_SETUP.md](NPCAP_SETUP.md) - Windows npcap driver installation guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed feature usage instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [NETWORK_SETUP.md](NETWORK_SETUP.md) - Network interface configuration guide

## Architecture

The platform consists of:
- **Backend**: Python Flask API with Scapy for packet capture
- **Frontend**: Modern web interface with real-time updates
- **Data Format**: PCAP files for packet storage and replay
- **Algorithms**: Optimized pattern matching for packet analysis

## System Architecture

```
┌─────────────────────────────────────────┐
│     Web Browser (Frontend)              │
│  - Real-time Packet Display             │
│  - Filter Controls                      │
│  - Statistics & Pie Charts              │
└────────────────────┬────────────────────┘
                     │ HTTP/JSON
┌────────────────────▼────────────────────┐
│  Flask API Server (Backend)             │
│  - Packet Capture Manager               │
│  - Filter Engine                        │
│  - Statistics Calculator                │
│  - Ruleset Comparison Engine            │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│  Scapy / System Tools                   │
│  - Network Interface Detection          │
│  - Raw Packet Capture (npcap/libpcap)   │
│  - PCAP File Handling                   │
└─────────────────────────────────────────┘
```

## License

See project documentation for license information.

## Troubleshooting

For common issues and their solutions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

If you encounter problems:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for your issue
2. Ensure npcap (Windows) or libpcap (Linux) is installed
3. Run with administrator/sudo privileges
4. Check that port 5000 is not in use