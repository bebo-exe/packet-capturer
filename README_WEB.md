# Wireshark Web - Browser-Based Packet Analyzer

A powerful, real-time network packet capture and analysis tool that runs in your browser. This is a web-based alternative to Wireshark with a modern, responsive interface.

## Features

✨ **Live Packet Capture** - Real-time monitoring of network traffic  
🔍 **Advanced Filtering** - Filter packets by protocol, source, destination  
📊 **Statistics Dashboard** - View protocol distribution and packet rates  
🎨 **Modern UI** - Beautiful dark theme with responsive design  
📥 **Export Functionality** - Save captured packets as PCAP files  
🌐 **Multi-Protocol Support** - TCP, UDP, DNS, HTTP/HTTPS, ARP, ICMP, Ethernet  
⚡ **Fast Performance** - Efficient packet parsing and display  
🎯 **ICMP Ping Capture** - Full support for ICMP Echo Request/Reply packets  
🔎 **Algorithm Comparison** - Ruleset experiment with quick search, Boyer-Moore, and KMP  

## Requirements

- Python 3.7+
- **npcap driver** (Windows) - REQUIRED for packet capture
- Network interface access (requires Administrator/sudo privileges)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## ⚠️ Critical: Install npcap (Windows Only)

The application requires **npcap** to capture packets on Windows.

**Before doing anything else:**

1. Download from: https://nmap.org/npcap/
2. Run installer as Administrator
3. **Select "Install npcap in WinPcap API-compatible mode"** (IMPORTANT!)
4. Complete installation and restart your computer

👉 See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed instructions

If you skip this step, you'll get an error like:
```
ERROR: Capture error: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed
```

## Installation

### 1. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install scapy>=2.5.0
pip install python-dotenv>=1.0.0
```

### 3. Run the Application

**Windows** (Command Prompt as Administrator):
```bash
python app.py
```

You should see:
```
✓ npcap found at: C:\Windows\System32\npcap\wpcap.dll
✓ Found X network interface(s)
📡 Starting Flask server...
   URL: http://localhost:5000
```

**macOS/Linux**:
```bash
sudo python app.py
```

The application will start at `http://localhost:5000`

## Usage Guide

### Starting a Capture

1. **Select Network Interface**: Choose from the dropdown menu (your network card)
2. **Optional Filter**: Type a filter term (TCP, UDP, DNS, HTTP, HTTPS, ICMP, ARP, etc.)
3. **Click Start**: Begin capturing packets in real-time
4. **Click Stop**: End the capture session

### Viewing Packets

- **Packet List**: Shows all captured packets with:
  - Packet number
  - Timestamp
  - Source IP/MAC
  - Destination IP/MAC
  - Protocol type

- **Click on any packet** to see detailed layer-by-layer information:
  - Ethernet/IP headers
  - TCP/UDP port information
  - ICMP details
  - ARP resolution data

### Using Quick Filters

Click the quick filter buttons in the sidebar to instantly filter:
- **TCP**: All TCP traffic
- **UDP**: All UDP traffic
- **ICMP**: All ICMP/ping traffic
- **ARP**: All ARP requests/responses

### Statistics

The dashboard shows:
- **Total Packets**: Number of packets captured
- **Protocols**: Count of different protocol types
- **Packets/sec**: Real-time capture rate

### Exporting Data

Click **Export JSON** to download all captured packets in JSON format for:
- Further analysis
- Data archival
- Integration with other tools

## Features Explained

### Protocol Support

- **IPv4/IPv6**: Internet Protocol analysis
- **TCP**: Transmission Control Protocol with port and flags
- **UDP**: User Datagram Protocol with port information
- **ICMP**: Internet Control Message Protocol
- **ARP**: Address Resolution Protocol
- **Ethernet**: Link layer information

### Layer-by-Layer Analysis

Each packet displays detailed information for each network layer:

```
Ethernet II
├── Source MAC
├── Destination MAC
└── Frame Type

Internet Protocol Version 4 (IPv4)
├── Source IP
├── Destination IP
├── TTL
├── Protocol
└── Flags

Transmission Control Protocol
├── Source Port
├── Destination Port
├── Sequence Number
├── Acknowledgment Number
├── Flags
└── Window Size
```

## API Endpoints

The Flask backend provides REST API endpoints:

- `GET /api/interfaces` - List network interfaces
- `POST /api/start-capture` - Start capturing packets
- `POST /api/stop-capture` - Stop capture
- `GET /api/packets` - Get captured packets
- `GET /api/packet/<id>` - Get packet details
- `GET /api/stats` - Get statistics
- `GET /api/export` - Export packets as JSON

## Command Line Usage

### Start with Admin Privileges (Required)

**Windows**:
```bash
# Run Command Prompt as Administrator, then:
python app.py
```

**macOS/Linux**:
```bash
sudo python app.py
```

### Test Dashboard

```bash
# Without capturing (for testing, doesn't need admin):
python -c "from flask import Flask; Flask(__name__).run(debug=True)"
```

## Troubleshooting

### "Permission Denied" Error

**Solution**: Run with administrator/root privileges
- Windows: Run Command Prompt or PowerShell as Administrator
- macOS/Linux: Use `sudo python app.py`

### No Interfaces Found

**Solution**: Check network connectivity
```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
```

### Capture Not Working

1. Check if admin privileges are enabled
2. Ensure no other packet capture tools are using the interface
3. Try selecting a different network interface
4. Check firewall settings

### Can't Connect to Backend

1. Ensure Flask is running on `http://localhost:5000`
2. Check if port 5000 is available (not blocked by firewall)
3. Try accessing `http://127.0.0.1:5000` instead

## Performance Tips

- **Limit packets**: The interface displays max 1000 packets (auto-clearing oldest)
- **Use filters**: Filter to specific protocols for focused analysis
- **Clear data**: Periodically clear captured packets to free memory
- **Close details panel**: When not needed, to reduce rendering overhead

## Advanced Usage

### Custom Packet Parsing

Edit the `PacketAnalyzer` class in `app.py` to add support for:
- Application layer protocols (HTTP, DNS, SSH, etc.)
- Custom headers
- Payload analysis

### Real-time Alerts

Modify the `packet_callback()` function to trigger alerts for:
- Suspicious traffic patterns
- Specific IP addresses
- Port scanning attempts

### PCAP Export

Extend the export functionality to save in PCAP format for import into Wireshark:

```python
# Add to app.py to save PCAP files
import pcapy
packet_capture.dump('capture.pcap')
```

## Project Structure

```
.
├── app.py                    # Flask backend with packet capture engine
├── templates/
│   └── index.html           # Web UI
├── requirements.txt         # Python dependencies
├── captures/                # Captured packet files
├── README.md                # This file
├── SETUP.md                 # Setup guide
└── QUICKSTART.md            # Quick start guide
```

## Security Notes

⚠️ **Important**: 
- This tool captures all network traffic on the selected interface
- Run only in trusted environments
- Be aware of encryption - HTTPS/SSH traffic is encrypted
- Network administrators may have policies against packet capture

## Future Enhancements

- 🔐 HTTPS/TLS decryption (with key logging)
- 📱 Mobile app version
- 🔔 Real-time alerts and notifications
- 📈 Advanced graphing and analytics
- 🌐 DNS resolution and IP geolocation
- 💾 PCAP file import/export
- 🎯 Deep packet inspection (DPI)
- 🚨 Intrusion detection patterns

## License

Open Source - Feel free to use and modify

## Support

For issues or questions:
1. Check this README
2. Review TROUBLESHOOTING section
3. Check SETUP.md for installation help

## Version

**Wireshark Web v1.0**
- Real-time packet capture
- Web-based interface
- Modern analytics dashboard
- Export functionality

---

**Happy packet analyzing!** 🚀
