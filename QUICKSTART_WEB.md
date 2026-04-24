# Quick Start Guide - Wireshark Web

Get up and running in 5 minutes!

## ⚠️ CRITICAL FIRST STEP: Install npcap

The application requires npcap to capture packets. **Do this first:**

1. Download from: **https://nmap.org/npcap/**
2. Run the installer as Administrator
3. **Select "Install npcap in WinPcap API-compatible mode"**
4. Complete installation and restart your computer

👉 See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed instructions if you need help.

---

## Step 1: Install Dependencies (1 min)

```bash
pip install Flask==2.3.3 Flask-CORS==4.0.0 scapy>=2.5.0 python-dotenv>=1.0.0
```

## Step 2: Run the Application (30 sec)

**Windows** (run Command Prompt as Administrator):
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

## Step 3: Open in Browser (10 sec)

Navigate to: **http://localhost:5000**

You should see the Wireshark Web interface!

## Step 4: Start Capturing (30 sec)

1. Click the **Network Interface** dropdown
2. Select your network interface (usually the first one)
3. Click the **▶ Start** button
4. Packets will start appearing in real-time!

## Examples

### Capture All Traffic
- Leave the filter empty
- Click Start

### Capture Only TCP Traffic
- Type "TCP" in the filter
- Click Start

### View Packet Details
- Click any packet in the list
- Details appear below with all layers

### Export Packets
- Click **📥 Export JSON**
- All captured packets are saved as JSON file

## Keyboard Shortcuts

- Press F5 to refresh the page
- Close the browser to stop viewing (data is still captured in backend)
- Ctrl+L to select all in address bar

## Common Tasks

### I see "Permission Denied"
→ Run as Administrator (Windows) or use `sudo` (macOS/Linux)

### No packets appearing
→ Make sure an interface is selected and Start button is clicked

### Want to try without capturing?
→ Just open the page and the UI will work (no actual capture without clicking Start)

### How to analyze captured packets?
→ Click any packet in the list to see detailed breakdown

## What's Next?

- Read [README_WEB.md](README_WEB.md) for full feature documentation
- Check [README_GUI.md](README_GUI.md) for GUI details
- Review [SETUP.md](SETUP.md) for advanced setup

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't access localhost:5000 | Check if Flask is running, try refreshing browser |
| No network interfaces showing | Run with admin/root privileges |
| App crashes at startup | Install all dependencies with pip |
| Packets not capturing | Select an interface from dropdown before clicking Start |

That's it! You're now ready to analyze network traffic like Wireshark but in your browser! 🎉
