# Packet Analyzer - Setup & Usage Guide

## Quick Start (Recommended)

### Step 1: Prerequisites
- Windows 10/11 (Linux/macOS support available with minor changes)
- Python 3.8+ installed
- **Administrator privileges** (required for packet capture)
- **npcap driver installed** (IMPORTANT - see section below)

### ⚠️ IMPORTANT: Install npcap First

Before running the application, you **MUST** install npcap:

1. Download from: **https://nmap.org/npcap/**
2. Run the installer as Administrator
3. **Select "Install npcap in WinPcap API-compatible mode"** during installation
4. Restart your computer
5. Run the application as Administrator

**If you skip this step, you will get an error like:**
```
ERROR: Capture error: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed
```

👉 **See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed npcap installation instructions**

### Step 2: Install & Setup (One-Time)

```powershell
# Open PowerShell as Administrator
# Navigate to the project folder
cd c:\Users\Lenovo\Desktop\templates

# Create virtual environment (if not already done)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Server

```powershell
# Make sure you're in the project directory
cd c:\Users\Lenovo\Desktop\templates

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Flask server
python app.py
```

You should see:
```
✓ Scapy imported successfully
✓ Found 10 network interface(s)
📡 Starting Flask server...
   URL: http://localhost:5000
   Running on http://127.0.0.1:5000
   Running on http://192.168.100.15:5000
```

### Step 4: Open in Browser

**Choose one of these URLs based on where you're accessing from:**

| URL | Use When |
|-----|----------|
| `http://localhost:5000` | Same computer |
| `http://127.0.0.1:5000` | Same computer (loopback) |
| `http://192.168.100.15:5000` | **Other computer on same network** ← WiFi Router Connection |

**Example:** If you want to open it from another computer on your network (like your phone or another PC):
- Replace `192.168.100.15` with your actual WiFi IP (shown in Flask output)
- Open `http://192.168.100.15:5000` in that computer's browser

---

## Troubleshooting

### Problem: "Failed to load network interfaces: Failed to fetch"

**Solution 1: Check Flask is Running**
```powershell
# Test if server is responding
curl http://localhost:5000/api/interfaces
```
You should get JSON with network adapters.

**Solution 2: Check Firewall**
- Windows Defender Firewall might block access from other computers
- Go to: Settings → Privacy & Security → Firewall & Network Protection → Allow an app through firewall
- Select Python and click "Change settings"
- Check "Private" and "Public" boxes

**Solution 3: Use Correct IP Address**
- Flask shows all available IPs at startup
- Use `http://192.168.100.15:5000` instead of `localhost` from other computers
- Do NOT use same IP twice - each access must use the IP shown for that network

**Solution 4: Browser Cache**
- Hard refresh: `Ctrl+Shift+Delete` then reload page
- Or open in Incognito mode

**Solution 5: Check Administrator Privileges**
- Open PowerShell as Administrator (right-click → Run as administrator)
- Run `python app.py`
- This is REQUIRED for packet capture to work

---

## Features

### 1. Network Interface Detection
- Automatically detects all adapters (WiFi, Ethernet, Loopback, Virtual)
- Shows friendly names and IPs
- Includes Intel Wireless-AC 9560 and VirtualBox adapters

### 2. Live Packet Capture
- Real-time packet monitoring
- Protocol detection (TCP, UDP, DNS, HTTP, HTTPS, ICMP, ARP)
- Packet statistics dashboard
- Shows source/destination and packet size

### 3. Interface Types Detected
- **WiFi (Wireless)**: Your main WiFi router connection (192.168.100.15)
- **Ethernet**: Virtual network adapters
- **Loopback**: Local testing (127.0.0.1)
- **Virtual**: VMware adapters (VMnet1, VMnet8)

---

## Performance & Limits

### Packet Display
- **Display Limit**: All captured packets are displayed in real-time (no limit on display)
- **Storage Limit**: Maximum **1000 packets** stored in memory
- **Scrolling**: Packet list is scrollable for viewing all captured packets
- **Update Frequency**: Packets update every 1 second

### When Capturing More Than 1000 Packets
- Oldest packets are automatically removed from memory
- Total count shown in statistics reflects remaining packets
- Most recent packets are always available

### Performance Tips
- Use Ethernet or WiFi (faster capture) instead of Loopback
- Close other network-heavy applications during capture
- If UI becomes slow with 1000+ packets, consider:
  - Using multiple smaller captures instead of one large capture
  - Filtering to specific protocols
  - Using browser DevTools (F12) to monitor memory usage

---

## API Endpoints

### `/api/interfaces` (GET)
Returns list of available network interfaces
```json
{
  "success": true,
  "count": 6,
  "interfaces": [
    {
      "name": "Wi-Fi",
      "friendly_name": "Wi-Fi",
      "type": "WiFi (Wireless)",
      "ip": "192.168.100.15(Preferred)"
    }
  ]
}
```

### `/api/start-capture` (POST)
Start capturing packets on selected interface
```json
{
  "interface": "Wi-Fi",
  "count": 100
}
```

### `/api/stop-capture` (POST)
Stop packet capture

### `/api/packets` (GET)
Get captured packets (updates in real-time)

### `/api/stats` (GET)
Get packet statistics (counts by protocol)

### `/api/test` (GET)
Simple health check

---

## From Another Computer on Your Network

### Windows PC / Laptop:
1. Find Flask server's IP: Look at Flask output for `192.168.x.x` address
2. Open browser
3. Go to: `http://192.168.100.15:5000` (use the IP shown in Flask)
4. Should load without errors

### Smartphone (Android/iPhone):
1. Connect to same WiFi as PC running Packet Analyzer
2. Open mobile browser
3. Go to: `http://192.168.100.15:5000`
4. Should load perfectly

### Requirements for Network Access:
- ✅ Both devices on same WiFi network
- ✅ No firewall blocking (allow Python through Windows Firewall)
- ✅ Flask server running with `-h 0.0.0.0` (default)
- ✅ Use the IP address Flask shows, not `localhost`

---

## Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| "Connection refused" | Flask not running | Run `python app.py` |
| "Failed to fetch" | Admin privileges missing | Run PowerShell as Administrator |
| "No interfaces found" | Scapy/Npcap not installed | Run `pip install -r requirements.txt` |
| "0 packets captured" | Interface has no traffic | Try loopback interface for testing |
| "Can't access from other PC" | Firewall blocking | Allow Python through Windows Firewall |

---

## File Structure

```
c:\Users\Lenovo\Desktop\templates\
├── app.py                    # Flask backend (main server)
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web UI (accessible via browser)
├── captures/                # Captured packets storage
└── .venv/                   # Virtual environment (auto-created)
```

---

## Requirements

See `requirements.txt`:
- Flask==2.3.3 (Web server)
- Flask-CORS==4.0.0 (Cross-origin requests)
- scapy>=2.5.0 (Packet capture)
- Werkzeug==2.3.7 (Web framework)
- python-dotenv>=1.0.0 (Environment variables)

---

## Performance Notes

- Packet capture runs in background thread
- Real-time updates via JavaScript polling (every 1-2 seconds)
- Supports 100-10,000 packet capture targets
- Can capture on any active interface simultaneously

---

## Next Steps

1. ✅ Run `python app.py` in Administrator PowerShell
2. ✅ Open `http://localhost:5000` in browser
3. ✅ Select WiFi interface (192.168.100.15)
4. ✅ Click "▶ Start" to begin capture
5. ✅ View live packets and statistics

**Enjoy packet sniffing! 🎉**
