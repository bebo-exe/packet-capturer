#!/usr/bin/env python3
"""
Simple Packet Capturer Script
Captures network packets and displays relevant information
Saves captured packets to a PCAP file on exit
"""

from scapy.all import sniff, IP, IPv6, TCP, UDP, ICMP, ARP, wrpcap
import argparse
import sys
from datetime import datetime

# Global list to store captured packets
captured_packets = []

def packet_callback(packet):
    """Process and display packet information"""
    global captured_packets
    
    try:
        # Store packet in global list
        captured_packets.append(packet)
        
        # Extract basic layer information
        if packet.haslayer(IP):
            ip_layer = packet[IP]
            print(f"\n{'='*60}")
            print(f"IP Packet Captured")
            print(f"Source IP: {ip_layer.src}")
            print(f"Destination IP: {ip_layer.dst}")
            print(f"Protocol: {ip_layer.proto}")
            
            # TCP Layer
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                print(f"TCP - Source Port: {tcp_layer.sport}, Dest Port: {tcp_layer.dport}")
                print(f"Flags: {tcp_layer.flags}")
            
            # UDP Layer
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                print(f"UDP - Source Port: {udp_layer.sport}, Dest Port: {udp_layer.dport}")
            
            # ICMP Layer
            elif packet.haslayer(ICMP):
                icmp_layer = packet[ICMP]
                print(f"ICMP - Type: {icmp_layer.type}, Code: {icmp_layer.code}")
        
        # IPv6 Packets
        elif packet.haslayer(IPv6):
            ipv6_layer = packet[IPv6]
            print(f"\n{'='*60}")
            print(f"IPv6 Packet Captured")
            print(f"Source IP: {ipv6_layer.src}")
            print(f"Destination IP: {ipv6_layer.dst}")
        
        # ARP Packets
        elif packet.haslayer(ARP):
            arp_layer = packet[ARP]
            print(f"\n{'='*60}")
            print(f"ARP Packet Captured")
            print(f"Operation: {arp_layer.op}")
            print(f"Source MAC: {arp_layer.hwsrc}, IP: {arp_layer.psrc}")
            print(f"Dest MAC: {arp_layer.hwdst}, IP: {arp_layer.pdst}")
        
    except Exception as e:
        print(f"Error processing packet: {e}")

def save_pcap_file(output_file):
    """Save captured packets to a PCAP file"""
    global captured_packets
    
    if captured_packets:
        try:
            wrpcap(output_file, captured_packets)
            print(f"\n✓ Saved {len(captured_packets)} packets to {output_file}")
        except Exception as e:
            print(f"Error saving PCAP file: {e}")
    else:
        print("\nNo packets were captured.")

def main():
    parser = argparse.ArgumentParser(description="Simple Packet Capturer with PCAP Export")
    parser.add_argument("-i", "--interface", help="Network interface to capture on (default: all)")
    parser.add_argument("-c", "--count", type=int, default=0, 
                        help="Number of packets to capture (0 = infinite)")
    parser.add_argument("-f", "--filter", default="", 
                        help="BPF filter (e.g., 'tcp port 80' or 'icmp')")
    parser.add_argument("-o", "--output", default="", 
                        help="Output PCAP filename (default: auto-generated with timestamp)")
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"capture_{timestamp}.pcap"
    
    try:
        print("Starting packet capture...")
        if args.count > 0:
            print(f"Capturing {args.count} packets")
        else:
            print("Capturing packets indefinitely (Ctrl+C to stop)")
        
        if args.filter:
            print(f"Using filter: {args.filter}")
        
        print(f"Output file: {args.output}")
        print("="*60)
        
        # Start sniffing packets
        sniff(
            iface=args.interface,
            prn=packet_callback,
            filter=args.filter,
            count=args.count if args.count > 0 else 0,
            store=False
        )
        
    except PermissionError:
        print("Error: This script requires administrator/root privileges!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nPacket capture stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Save PCAP file when exiting
        save_pcap_file(args.output)

if __name__ == "__main__":
    main()