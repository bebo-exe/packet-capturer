# Packet Analyzer - Setup & Usage Guide

## Prerequisites (All Platforms)

- **Python 3.8+** installed
- **Administrator/sudo privileges** (required for packet capture)
- Modern web browser (Chrome, Firefox, Edge, Safari)
- **Platform-specific requirements** (see sections below)

---

## Windows Setup & Running

### Prerequisites (Windows)
- Windows 10/11
- **npcap driver** (REQUIRED - see npcap section below)

### Step 1: Install npcap (Windows ONLY)

**⚠️ CRITICAL: You MUST install npcap before running the application**

1. Download from: **https://nmap.org/npcap/**
2. Run the installer as Administrator
3. **During installation, select: "Install npcap in WinPcap API-compatible mode"** ← **IMPORTANT!**
4. Complete the installation
5. **Restart your computer**

**If npcap is not installed, you'll get this error:**
```
ERROR: Capture error: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed
```

👉 **See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed npcap installation with screenshots**

### Step 2: Create Virtual Environment (Recommended)

```powershell
# Open PowerShell as Administrator
# Navigate to project folder
cd C:\path\to\packet-capturer-main

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Application (Windows)

```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Run the application
python app.py
```

You should see:
```
✓ Scapy imported successfully
✓ npcap found at: C:\Windows\System32\npcap\wpcap.dll
✓ Found X network interface(s)
📡 Starting Flask server...
   URL: http://localhost:5000
   API: http://localhost:5000/api/test
```

### Step 4: Open in Browser (Windows)

Navigate to: **`http://localhost:5000`**

---

## Linux Setup & Running

### Prerequisites (Linux)

- **libpcap development files** (required by Scapy)
- **sudo access** for packet capture

### Step 1: Install System Dependencies (Linux)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libpcap-dev python3-dev python3-pip
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install -y libpcap-devel python3-devel python3-pip
```

**Arch:**
```bash
sudo pacman -S libpcap python3 python-pip
```

### Step 2: Create Virtual Environment (Recommended)

```bash
cd /path/to/packet-capturer-main

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Application (Linux)

**Option A: Using Full Path (Recommended)**
```bash
# This avoids PATH issues with sudo
sudo /path/to/packet-capturer-main/.venv/bin/python app.py

# Example:
sudo /home/username/Desktop/packet-capturer-main/.venv/bin/python app.py
```

**Option B: Using Launcher Script**
```bash
# Make run.sh executable (one-time)
chmod +x run.sh

# Run the app
./run.sh
```

**Option C: Without Virtual Environment**
```bash
sudo python3 app.py
```

You should see:
```
✓ Scapy imported successfully
✓ Found X network interface(s)
📡 Starting Flask server...
   URL: http://localhost:5000
   API: http://localhost:5000/api/test
```

### Step 4: Open in Browser (Linux)

Navigate to: **`http://localhost:5000`**

---

## macOS Setup & Running

### Prerequisites (macOS)

- macOS 10.13+
- **Python 3.8+** (via Homebrew recommended)
- **sudo access** for packet capture

### Step 1: Install Python (macOS)

If you don't have Python 3.8+, install via Homebrew:

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Verify installation
python3 --version
```

### Step 2: Create Virtual Environment (Recommended)

```bash
cd /path/to/packet-capturer-main

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Application (macOS)

**Option A: Using Full Path (Recommended)**
```bash
# This avoids PATH issues with sudo
sudo /path/to/packet-capturer-main/.venv/bin/python app.py

# Example:
sudo /Users/username/Desktop/packet-capturer-main/.venv/bin/python app.py
```

**Option B: Using Launcher Script**
```bash
# Make run.sh executable (one-time)
chmod +x run.sh

# Run the app
./run.sh
```

**Option C: Without Virtual Environment**
```bash
sudo python3 app.py
```

You should see:
```
✓ Scapy imported successfully
✓ Found X network interface(s)
📡 Starting Flask server...
   URL: http://localhost:5000
   API: http://localhost:5000/api/test
```

### Step 4: Open in Browser (macOS)

Navigate to: **`http://localhost:5000`**

---

## Installation & Running Troubleshooting

### General Installation Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No module named 'scapy'" | Scapy not installed | Run `pip install -r requirements.txt` in activated venv |
| "Permission denied" | Missing sudo/admin privileges | Run with `sudo` (Linux/macOS) or as Administrator (Windows) |
| "Python command not found" | Python not in PATH | Use `python3` instead of `python` on Linux/macOS |
| "pip: command not found" | pip not installed | Install pip: `python -m pip install --upgrade pip` |

### Platform-Specific Issues

#### Windows Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "winpcap is not installed" | npcap not installed | Follow Windows Step 1: Install npcap |
| "ERROR at offset X in the MZ header" | Wrong Python bitness vs npcap | Ensure Python bitness (32/64-bit) matches npcap |
| "Access denied" | Not running as Administrator | Right-click PowerShell, select "Run as administrator" |

#### Linux/macOS Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "libpcap.so not found" | libpcap-dev not installed | Run `sudo apt-get install libpcap-dev` (Linux) |
| "Operation not permitted" | Missing sudo privileges | Run with `sudo` prefix |
| "/bin/bash: python: command not found" | Using `python` instead of `python3` | Use `python3` for Python 3.x |

---

## Runtime Issues & Troubleshooting

### Packet Capture Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No interfaces found" | Scapy/npcap detection issue | Restart application as Administrator/sudo |
| "0 packets captured" | No network traffic on interface | Try WiFi interface instead of Loopback |
| "Capture hangs without showing packets" | Firewall blocking capture | Disable Windows Firewall or allow Python |
| "Connection refused" | Flask server not running | Ensure `python app.py` completed without errors |

### API/Browser Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Failed to load network interfaces" | API server not responding | Check Flask server output, ensure running on port 5000 |
| "Blank page in browser" | Template not found | Ensure `templates/index.html` exists in project directory |
| "CORS error in console" | Cross-origin request issue | API already configured with CORS (should not occur) |
| "Updates not refreshing" | JavaScript fetch errors | Check browser console (F12) for specific errors |

### File/Directory Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "PCAP file not saved" | Permission denied in working directory | Create `captures/` directory or run from different location |
| "Cannot find pcap file" | File saved in working directory, not project dir | Check `python app.py` output for capture file location |

---

## Access from Other Computers on Network

**All Platforms**: When Flask starts, it displays all available IP addresses:

```
📡 Starting Flask server...
   URL: http://localhost:5000
   Running on http://127.0.0.1:5000
   Running on http://192.168.100.15:5000  ← Use this to access from other computers
```

**From another computer on your network:**
- Replace `192.168.100.15` with the IP shown in Flask output
- Open `http://192.168.100.15:5000` in any web browser on your network

### Requirements for Network Access:
- ✅ Both devices on same WiFi network or same LAN
- ✅ No firewall blocking (allow Python through Windows Firewall on capturing PC)
- ✅ Flask server running with `-h 0.0.0.0` (default)
- ✅ Use the IP address Flask shows, not `localhost` or `127.0.0.1`

---

## Features Overview

### 1. Real-Time Packet Capture
- Captures all network packets on selected interface
- Continuous capture until user clicks "Stop"
- Displays packets as they arrive
- Shows live statistics (count, protocol distribution)

### 2. Multi-Protocol Support
- **IPv4/IPv6**: Internet Protocol
- **TCP**: Transmission Control Protocol with port detection
- **UDP**: User Datagram Protocol
- **ICMP**: Internet Control Message Protocol (Ping, errors)
- **ARP**: Address Resolution Protocol (MAC resolution)
- **HTTP/HTTPS**: Web traffic (automatic port-based detection)
- **DNS**: Domain Name System (port 53 detection)

### 3. Packet Information Display
For each captured packet, displays:
- **Packet Number**: Sequential ID in capture session
- **Timestamp**: Exact time packet was captured
- **Protocol**: TCP, UDP, ICMP, ARP, HTTP, HTTPS, DNS, or Unknown
- **Source IP**: Originating IP address
- **Destination IP**: Target IP address
- **Ports**: Source and destination ports (TCP/UDP only)
- **Payload Size**: Total packet size in bytes
- **Details**: Protocol-specific information (ICMP type, TCP flags, etc.)

### 4. Real-Time Statistics
Statistics dashboard updates in real-time and shows:
- **Total Packets**: All packets captured in current session
- **TCP Packets**: Count of TCP protocol packets
- **UDP Packets**: Count of UDP protocol packets
- **DNS Packets**: Count of DNS queries/responses
- **ARP Packets**: Count of ARP resolution requests
- **ICMP Packets**: Count of ICMP messages (ping, errors)

### 5. File Management
- **Save to PCAP**: Export captured packets in standard PCAP format
- **Load PCAP Files**: Analyze previously saved captures
- **PCAP Storage**: Default directory is `captures/` in project folder
- **PCAP Naming**: Auto-generated filename or custom name

### 6. Advanced Algorithm Comparison (Ruleset System)
Experiments with pattern-matching algorithms:
- Captures specified number of packets (minimum 1000 recommended)
- Selects one packet at random as search pattern
- Compares three algorithms:
  - **Quick Search**: Python's built-in `in` operator
  - **Boyer-Moore**: Skip-based pattern matching
  - **Aho-Corasick (KMP)**: Finite automaton approach
- Displays:
  - Number of matches found
  - Execution time in milliseconds
  - Expected time complexity

### 7. Network Interface Detection
Automatically detects all available interfaces:
- **WiFi Adapters**: Wireless network connections
- **Ethernet Adapters**: Wired network connections
- **Virtual Adapters**: VMware, VirtualBox, VPN
- **Loopback Interface**: Local testing (127.0.0.1)
- Shows adapter type, IP address, and MAC address

---

## Data Storage & Locations

### Capture Directory
By default, captured PCAP files are saved to:
- **Windows**: `C:\path\to\project\captures\`
- **Linux**: `/path/to/project/captures/`
- **macOS**: `/path/to/project/captures/`

### PCAP File Format
- **Standard Format**: All captures use libpcap/PCAP format
- **Compatible Tools**: Can be opened with:
  - Wireshark
  - tcpdump
  - Any PCAP analyzer

### Memory Management
- **Max Packets in Memory**: 1000 packets per session
- **Oldest Packet Removal**: When limit exceeded, oldest packet is removed
- **Total Count**: Shows total packets captured (even if display limited to 1000)

---

## API Endpoints Reference

### Get Network Interfaces
```
GET /api/interfaces
Response: { success, interfaces[], count }
```

### Start Packet Capture
```
POST /api/start-capture
Request: { interface, count, save_pcap, pcap_filename, filter }
Response: { success, message, interface, friendly_name, pcap_file }
```

### Stop Packet Capture
```
POST /api/stop-capture
Response: { success, message, pcap_file }
```

### Get Captured Packets
```
GET /api/packets
Response: { success, packets[], count, capturing }
```

### Get Statistics
```
GET /api/stats
Response: { success, total, protocols{}, capturing }
```

### Clear All Packets
```
POST /api/clear
Response: { success, message }
```

### Run Ruleset Experiment
```
POST /api/run-ruleset
Request: { interface, count, save_pcap, pcap_filename, filter }
Response: { success, chosen_index, chosen_summary, pattern_len, results{}, saved_pcap }
```

### Health Check
```
GET /api/test
Response: { status, message, packets_captured }
```

---

## Performance Optimization Tips

### For Faster Capture:
1. Use **Ethernet** or **WiFi** adapters instead of Loopback
2. **Close other network-heavy applications** before capture
3. **Disable VPN** or other packet-intercepting software
4. **Use specific interface** with high traffic
5. **Run on wired network** for more consistent traffic

### For Better GUI Performance:
1. Limit captured packets to 500-1000 for faster rendering
2. Avoid capturing on high-traffic networks for extended periods
3. **Clear captured packets** between sessions
4. Use browser **DevTools (F12) → Performance** to monitor memory
5. For very long captures, use **multiple smaller captures** instead

### For Ruleset Experiments:
1. **Start with 1000-3000 packets** for reasonable timing comparisons
2. **Avoid 10000+ packets** on slower systems
3. **Run on local network** with moderate traffic
4. Compare results across **multiple runs** for consistency

---

## Quick Reference Table

| Task | Windows | Linux | macOS |
|------|---------|-------|-------|
| Install deps | `pip install -r requirements.txt` | `sudo apt install libpcap-dev` + `pip install -r requirements.txt` | `brew install libpcap` + `pip install -r requirements.txt` |
| Create venv | `python -m venv .venv` | `python3 -m venv .venv` | `python3 -m venv .venv` |
| Activate venv | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` | `source .venv/bin/activate` |
| Run app | `python app.py` | `sudo /path/to/.venv/bin/python app.py` | `sudo /path/to/.venv/bin/python app.py` |
| Browser | `http://localhost:5000` | `http://localhost:5000` | `http://localhost:5000` |
| Special setup | Install npcap | Install libpcap-dev | None (macOS included) |

---

## Next Steps After Installation

1. ✅ Follow the setup instructions for your OS above
2. ✅ Open `http://localhost:5000` in your browser
3. ✅ **Select a Network Interface** (try WiFi or Ethernet)
4. ✅ **Click "▶ Start"** to begin packet capture
5. ✅ Watch packets appear in real-time
6. ✅ View statistics on the right panel
7. ✅ Click **"⏹ Stop"** to end capture
8. ✅ **Optionally save capture** to PCAP file

---

## Support & Additional Resources

For more information:
- See [README.md](README.md) for full feature overview
- See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed npcap installation (Windows)
- See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed feature usage
- See [NETWORK_SETUP.md](NETWORK_SETUP.md) for network configuration
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for additional help

---

**Last Updated**: May 2026
