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

## Access from Other Computers on Network

**All Platforms**: When Flask starts, it displays all available IP addresses:

```
📡 Starting Flask server...
   URL: http://localhost:5000
   Running on http://127.0.0.1:5000
   Running on http://<IP_ADDRESS>:5000  ← Use this to access from other computers
```

**From another computer on your network:**
- Replace the IP address with the IP shown in Flask output
- Open `http://<IP_ADDRESS>:5000` in any web browser on your network

### Requirements for Network Access:
- ✅ Both devices on same WiFi network or same LAN
- ✅ No firewall blocking (allow Python through Windows Firewall on capturing PC)
- ✅ Flask server running with `-h 0.0.0.0` (default)
- ✅ Use the IP address Flask shows, not `localhost` or `127.0.0.1`

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
