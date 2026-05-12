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
4. Navigate to your folder: `cd C:\path\to\packet-capturer`
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
cd /d C:\path\to\packet-capturer
.\.venv\Scripts\activate.bat
python app.py
pause
```

Right-click → Run as administrator

## Step 3: macOS/Linux Users - Use sudo

```bash
cd ~/path/to/packet-capturer
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

## Step 8: Reinstall Dependencies

Sometimes pip packages get corrupted:

```bash
pip install --force-reinstall Flask==2.3.3 Flask-CORS==4.0.0 scapy python-dotenv
```

## Step 9: Full Reset

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

---

## ❌ Ruleset Experiment Issues

### Problem: "No pattern found" in ruleset results

The pattern extraction failed, usually because packets have no usable payload data.

**Causes:**
1. **Captured packets have no application layer data** (e.g., only ARP packets)
   - ARP packets don't have payload layer (Raw)
   - Try capturing from a web browser (generates HTTP/HTTPS with payloads)

2. **Payload data is too small or random**
   - Some protocols send tiny packets without repeating patterns
   - Solution: Capture more packets or different traffic

**Solutions:**
- Open a web browser and visit a few websites during packet capture
- Use DNS queries (generates repeated DNS response patterns)
- Try capturing file downloads (larger payloads with patterns)
- Ensure you're on an active network with application traffic

---

### Problem: Very low match counts (0-5 matches)

The pattern was found, but matches are unrealistically low.

**This should NOT happen with payload-only search**, but if it does:

**Check 1: Payload extraction working correctly**
- Pattern extraction now searches ONLY application payloads (Raw layer)
- Each captured packet's headers are unique, so we ignore them
- If match count is still very low, the payload itself may have no repeating patterns

**Solutions:**
1. **Capture different traffic**
   - Web browsing creates repeating HTTP headers and content
   - DNS queries create identical response patterns
   - Video streaming has repeating data blocks

2. **Increase packet count**
   - Captured 1000 packets? Try 2000-3000
   - More packets = higher chance of repeating payload patterns
   - Different conversations may have different patterns

3. **Check packet types**
   - Click on captured packets in the table
   - Look at "Frame Data" field
   - If you see mostly control packets (ARP, SYN, FIN), pattern will be scarce
   - Wait for packets with actual data (HTTP, DNS responses)

---

### Problem: Ruleset buttons work but clicking "Run" shows error

**Error: "Failed to fetch" when running ruleset**
- Backend didn't receive the request
- Check: Is Flask still running in the terminal?
- Check: Did Flask crash? Look for error messages
- Solution: Restart Flask and try again

**Error: "Network error in response"**
- Backend received request but had an error
- Check `packet_capture.log` file for detailed error
- Common: Pattern extraction failed (see "No pattern found" section above)

**Error: Results table shows "undefined" values**
- Backend returned malformed response
- Check terminal output for Python errors
- Hard refresh browser and try again

---

### Problem: Ruleset results don't update

Running experiment twice shows same results.

**This is normal!** Each run extracts a NEW pattern:
- 1st run: Extracts pattern from packet at random index
- 2nd run: Extracts different pattern from different packet
- Results are intentionally random to show algorithm performance on different patterns

**Expected behavior:**
- Match counts may be different each time
- Execution times may vary by 10-20% based on system load
- Algorithm rankings should be consistent (Quick usually fastest, KMP/BM vary)

### Problem: Mode selection not persisting

Changed to Parallel mode, but sequential ran instead.

**Cause:** Browser cache or page refresh reset the mode.

**Solutions:**
1. **Hard refresh after selecting mode**
   - Select Parallel mode
   - WAIT 2 seconds (let JavaScript update)
   - Then click Run (don't refresh)

2. **Check button highlighting**
   - Parallel mode button should have green glow when selected
   - Sequential button should be dimmed
   - If buttons look wrong, page didn't load JavaScript properly
   - Hard refresh with Ctrl+Shift+R

3. **Check browser console**
   - Press F12 → Console
   - Any JavaScript errors?
   - Error: "Uncaught ReferenceError: rulesetMode is not defined"
   - Solution: Hard refresh page

---

## Ruleset Experiment Checklist

✓ Captured 1000+ packets?
✓ Capture includes application data (HTTP, DNS, etc)?
✓ Mode buttons visible and highlighting works?
✓ Click Run and wait for results table to appear?
✓ Results show reasonable match counts (5-50+ typically)?
✓ Try Parallel mode, compare timing to Sequential?
✓ Parallel should be faster (or similar) for 1000+ packets?
✓ Confirmation dialog appears after successful run?
