#!/usr/bin/env python3
"""Test packet capture with traffic generation"""
import urllib.request
import json
import time
import subprocess

def api_call(endpoint, method='GET', data=None):
    """Make API call"""
    url = f'http://localhost:5000{endpoint}'
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {'error': str(e)}

print("=" * 60)
print("PACKET CAPTURE TEST")
print("=" * 60)

# Start capture
print("\n[1] Starting capture on Wi-Fi...")
result = api_call('/api/start-capture', 'POST', json.dumps({
    'interface': 'Wi-Fi',
    'count': 200,
    'save_pcap': False
}).encode())
print(f"    Response: {result}")

# Generate traffic
print("\n[2] Generating test traffic...")
print("    - ICMP (ping 8.8.8.8 x5)")
subprocess.run(['ping', '-n', '5', '8.8.8.8'], capture_output=True, timeout=10)

print("    - DNS (nslookup google.com)")
subprocess.run(['nslookup', 'google.com'], capture_output=True, timeout=10)

print("    - Waiting 2 seconds...")
time.sleep(2)

# Get packets
print("\n[3] Fetching captured packets...")
result = api_call('/api/packets', 'GET')
count = result.get('count', 0)
packets = result.get('packets', [])

print(f"    Total packets: {count}")
print(f"\n    First 40 packets:")
for i, pkt in enumerate(packets[:40]):
    proto = pkt.get('protocol', 'Unknown')
    src = pkt.get('src_ip', '?')
    dst = pkt.get('dst_ip', '?')
    info = pkt.get('info', '')
    port_str = ""
    if pkt.get('src_port'):
        port_str = f":{pkt['src_port']}"
    if pkt.get('dst_port'):
        port_str += f" → :{pkt['dst_port']}"
    print(f"    [{i+1:2}] {proto:8} {src:18} {port_str:15} → {dst:18} {info}")

# Summary
print(f"\n    Protocol breakdown:")
protocols = {}
for pkt in packets:
    proto = pkt.get('protocol', 'Unknown')
    protocols[proto] = protocols.get(proto, 0) + 1

for proto in sorted(protocols.keys()):
    count_p = protocols[proto]
    print(f"      {proto:10}: {count_p:3}")

# Stop capture
print("\n[4] Stopping capture...")
result = api_call('/api/stop-capture', 'POST', b'{}')
print(f"    Response: {result}")

print("\n" + "=" * 60)
print("SUMMARY:")
if 'TCP' in protocols or 'UDP' in protocols or 'ICMP' in protocols or 'DNS' in protocols:
    print("✓ TCP/UDP/ICMP/DNS packets ARE being captured!")
else:
    print("✗ Only ARP packets captured - TCP/UDP/ICMP/DNS missing")
    print("  This indicates the BPF filter is working but not delivering expected packets")
    print("  OR the filter='ip or arp' is not passing TCP/UDP/ICMP")
print("=" * 60)
