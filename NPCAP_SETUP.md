# npcap Installation & Configuration Guide

## ❌ Error: "winpcap is not installed"

If you see this error:
```
ERROR:__main__:Capture error: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed. You may use conf.L3socket or conf.L3socket6 to access layer 3
[DEBUG] Capture exception: Sniffing and sending packets is not available at layer 2: 
winpcap is not installed
```

This means **npcap** is not installed on your system. This is the packet capture driver that Scapy needs to capture network packets.

---

## ✅ Solution: Install npcap

### Step 1: Download npcap

1. Go to: **https://nmap.org/npcap/**
2. Click **"Download npcap"**
3. Download the latest stable version (e.g., `npcap-1.73.exe`)

### Step 2: Run the Installer

1. Right-click the downloaded `.exe` file
2. Select **"Run as administrator"**
3. Click **"Next"** to proceed

### Step 3: Important Installation Settings

When you see the installation options screen:

**✅ REQUIRED: Check "Install npcap in WinPcap API-compatible mode"**

This option is critical! It allows Scapy to communicate with npcap properly.

The screen should look like:
```
☑ Install npcap in WinPcap API-compatible mode
☐ Install npcap in DLL-only mode
```

**Choose the first option (WinPcap API-compatible mode)**

### Step 4: Complete Installation

1. Click **"Install"**
2. Wait for installation to complete
3. Click **"Finish"**
4. **Restart your computer** (recommended, but you may try without restarting first)

### Step 5: Verify Installation

The application will check for npcap when it starts. You should see:

```
✓ npcap found at: C:\Windows\System32\npcap\wpcap.dll
```

If you don't see this, npcap was not installed correctly. Follow the steps again.

---

## 🔧 Troubleshooting npcap Installation

### Issue: "npcap is not installed" after installation

**Solution:**
1. Open **Control Panel** → **Programs and Features**
2. Find **npcap** in the list
3. Click **Uninstall**
4. Download the latest version from https://nmap.org/npcap/
5. Run the installer again as Administrator
6. **Make sure to select "WinPcap API-compatible mode"**
7. Restart your computer

### Issue: npcap.exe shows "Device driver not found"

**Solution:**
1. The installer needs to run as Administrator
2. Right-click the `.exe` file
3. Select "Run as administrator"
4. Complete the installation
5. Restart your computer

### Issue: Still getting the error after installation

**Solution:**
1. Make sure you ran the installer as Administrator
2. Make sure you selected "WinPcap API-compatible mode"
3. Restart your computer
4. Run `python app.py` as Administrator

---

## 📋 Verification Checklist

After installing npcap:

- [ ] npcap is listed in Control Panel → Programs and Features
- [ ] File exists: `C:\Windows\System32\npcap\wpcap.dll`
- [ ] Running app.py shows: `✓ npcap found at: ...`
- [ ] Running the app as Administrator
- [ ] No errors when starting capture

---

## 🚀 Running the Application

**Important:** After installing npcap, always run the application as Administrator:

### Option 1: Command Prompt (Administrator)
```powershell
# Right-click Command Prompt and select "Run as administrator"
cd C:\Users\Lenovo\Desktop\templates
python app.py
```

### Option 2: PowerShell (Administrator)
```powershell
# Right-click PowerShell and select "Run as administrator"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python app.py
```

### Option 3: Run CMD as Administrator directly
```batch
C:\Users\Lenovo\Desktop\templates> python app.py
```

---

## ℹ️ Why npcap is Needed

- **npcap** is a packet capture library for Windows (modern replacement for WinPcap)
- It allows applications to capture raw network packets
- Without it, Scapy cannot capture any packets
- It's required by Wireshark, nmap, and other network analysis tools

---

## 🔗 Useful Links

- **npcap Official Site**: https://nmap.org/npcap/
- **npcap GitHub**: https://github.com/nmap/npcap
- **Scapy Documentation**: https://scapy.readthedocs.io/
- **Wireshark**: Uses the same npcap driver

---

## ✅ After Installation

Once npcap is installed and you restart your computer:

1. Run the application as Administrator:
   ```
   python app.py
   ```

2. You should see:
   ```
   ✓ npcap found at: C:\Windows\System32\npcap\wpcap.dll
   ✓ Found X network interface(s)
   📡 Starting Flask server...
   ```

3. Open browser: `http://localhost:5000`

4. Select an interface and click **Start Capture**

5. The status should change to capturing (no errors!)

---

## 📞 Still Having Issues?

If npcap is installed but you still see errors:

1. **Run as Administrator** - This is the most common issue
   - Right-click Command Prompt/PowerShell
   - Select "Run as administrator"
   - Then run `python app.py`

2. **Check firewall** - Windows Firewall might block packet capture
   - Try disabling firewall temporarily to test
   - Or add an exception for Python

3. **Restart after npcap installation**
   - npcap needs a system restart to fully activate
   - Restart your computer after installation

4. **Check npcap is in correct location**
   - Should be at: `C:\Windows\System32\npcap\wpcap.dll`
   - Or: `C:\Program Files\npcap\wpcap.dll`

---

## 🎯 Summary

1. ✅ Install npcap from https://nmap.org/npcap/
2. ✅ Select "WinPcap API-compatible mode" during installation
3. ✅ Restart your computer
4. ✅ Run app as Administrator
5. ✅ Verify npcap is detected when app starts
6. ✅ Start capturing packets!

That's it! The application will now be able to capture ICMP and all other packet types.
