#!/usr/bin/env python3
"""Test script to debug Scapy interface availability"""

from scapy.all import get_if_list, conf, sniff
import sys

print("=" * 60)
print("SCAPY INTERFACE DEBUG")
print("=" * 60)

# List all interfaces
print("\n✓ Scapy get_if_list():")
interfaces = get_if_list()
for i, iface in enumerate(interfaces):
    print(f"  [{i}] {repr(iface)}")

print(f"\n✓ Total interfaces: {len(interfaces)}")
print(f"✓ Scapy conf.iface: {repr(conf.iface)}")

# Try to sniff on first non-loopback interface with short timeout
print("\n✓ Attempting 3-second sniff on first active interface...")
if interfaces:
    target_iface = interfaces[0]
    print(f"  Target interface: {repr(target_iface)}")
    
    packets_captured = []
    def callback(pkt):
        packets_captured.append(pkt)
        print(f"  [PACKET] {pkt.summary()}")
    
    try:
        sniff(iface=target_iface, prn=callback, store=False, timeout=3, filter="")
        print(f"\n✓ Sniff completed. Captured {len(packets_captured)} packets")
    except Exception as e:
        print(f"✗ Error during sniff: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ No interfaces found!")

print("\n" + "=" * 60)
