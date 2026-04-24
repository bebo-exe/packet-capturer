# Troubleshooting Guide

## ❌ Error: "winpcap is not installed" OR "Capture error: Sniffing and sending packets is not available"

**This is the most common error on Windows.**

### Problem
You see this error when trying to capture packets:
```
ERROR:__main__:Capture error: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed. You may use conf.L3socket or conf.L3socket6 to access layer 3
```

### Solution
**npcap is not installed.** You MUST install it before the application can capture any packets.

1. Download from: **https://nmap.org/npcap/**
2. Run the installer as Administrator
3. **IMPORTANT: Select "Install npcap in WinPcap API-compatible mode"**
4. Complete installation
5. **Restart your computer**
6. Run the application again as Administrator

**See [NPCAP_SETUP.md](NPCAP_SETUP.md) for detailed instructions.**

After installing npcap and restarting, you should see:
```
✓ npcap found at: C:\Windows\System32\npcap\wpcap.dll
```

If you still see the error after installation:
- Make sure you restarted your computer
- Make sure you ran the installer as Administrator
- Make sure you selected "WinPcap API-compatible mode"
- Try running the app.py as Administrator

---

## ❌ Error: "Error starting capture: Failed to fetch"

This error means the browser cannot connect to the Flask backend server.

## Step 1: Verify Flask is Running

Check if you see output like this in your terminal:

```
============================================================
Starting Wireshark Web Packet Analyzer
============================================================
Scapy Available: True
Network Interfaces Found: 5
  - eth0
  - eth1
  - ...
Starting Flask server on http://0.0.0.0:5000
Open your browser to: http://localhost:5000
============================================================
```

## Step 2: Windows Users - Run as Administrator

The most common cause is **not running with administrator privileges**.

### Option A: Run Command Prompt as Administrator
1. Press `Win + R`
2. Type: `cmd`
3. Press `Ctrl + Shift + Enter` (instead of just Enter)
4. Navigate to your folder: `cd C:\Users\Lenovo\Desktop\templates`
5. Activate venv: `.\.venv\Scripts\activate`
6. Run: `python app.py`

### Option B: Run PowerShell as Administrator
1. Right-click PowerShell
2. Select "Run as administrator"
3. Activate venv: `. .\.venv\Scripts\activate`
4. Run: `python app.py`

### Option C: Create Batch Script
Create a file named `run_app.bat`:
```batch
@echo off
cd /d C:\Users\Lenovo\Desktop\templates
.\.venv\Scripts\activate.bat
python app.py
pause
```

Right-click → Run as administrator

## Step 3: macOS/Linux Users - Use sudo

```bash
cd ~/Desktop/templates
source venv/bin/activate  # if using venv
sudo python app.py
```

## Step 4: Check Port 5000

If Flask says "Address already in use", kill the old process:

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :5000
kill -9 <PID>
```

Or just use a different port:
```bash
# Edit app.py, change port=5000 to port=5001
python app.py
# Then visit http://localhost:5001
```

## Step 5: Check Scapy Installation

Verify Scapy is installed:

```bash
python -c "from scapy.all import sniff; print('Scapy OK')"
```

If error, reinstall:
```bash
pip install --upgrade scapy
```

## Step 6: Check Browser Console

1. Open browser DevTools: `F12` or `Ctrl+Shift+I`
2. Click "Console" tab
3. Look for error messages like:
   - `Failed to fetch` → Backend not running
   - `CORS error` → Backend CORS issue (should be fixed now)
   - `net::ERR_CONNECTION_REFUSED` → Port is blocked
   - `net::ERR_NAME_NOT_RESOLVED` → Wrong URL

## Step 7: Test Backend Directly

Open your browser and visit:
```
http://localhost:5000/api/health
```

You should see JSON like:
```json
{
  "status": "ok",
  "version": "1.0",
  "scapy_available": true,
  "is_capturing": false,
  "total_packets": 0
}
```

If you get an error, the backend is not running properly.

## Step 8: Check Logs

Look for the log file:
```
C:\Users\Lenovo\Desktop\templates\packet_capture.log
```

Open it to see detailed error messages.

## Step 9: Reinstall Dependencies

Sometimes pip packages get corrupted:

```bash
pip install --force-reinstall Flask==2.3.3 Flask-CORS==4.0.0 scapy python-dotenv
```

## Step 10: Full Reset

If all else fails:

```bash
# Windows
rmdir /s .\.venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

```bash
# macOS/Linux
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo python app.py
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to fetch" | Backend not running or wrong port | Make sure Flask is running + admin privileges |
| "No interfaces found" | Not running with elevated privileges | Run as Administrator/sudo |
| "Port 5000 already in use" | Another app using port 5000 | Kill old process or change port |
| "scapy not found" | Scapy not installed | `pip install scapy` |
| "Permission denied" | Capture requires elevated privileges | Run with admin/sudo |
| "This site can't be reached" | Flask not responding | Check Flask logs in terminal |

## Verify Setup

Run the verification script:

```bash
python verify_setup.py
```

This will check:
- Python version ✓
- Package installation ✓
- Network interfaces ✓
- File structure ✓

## Success Indicator

When everything works, you should see:

1. ✅ Browser shows Wireshark Web interface with purple header
2. ✅ Network interface dropdown has values
3. ✅ Console shows "✓ Backend is running"
4. ✅ No error dialogs appear
5. ✅ You can click Start and packets appear

## Still Not Working?

Check the logs:

**Terminal output:**
- Shows stacktrace of what went wrong
- Shows which interface is being used
- Shows permission errors

**Log file:**
- `packet_capture.log` in the templates folder
- Contains all backend errors and debug messages

**Browser console (F12):**
- Shows fetch errors
- Shows JavaScript errors
- Shows network requests

Provide these when reporting issues!

---

**Quick Checklist:**
- [ ] Running as Administrator (Windows) or with sudo (macOS/Linux)
- [ ] Flask running (see "=====" banner in terminal)
- [ ] Can access http://localhost:5000 in browser
- [ ] /api/health returns JSON
- [ ] No error dialogs on page load
- [ ] Interface dropdown has items
- [ ] Click Start gives proper error messages (not "Failed to fetch")
