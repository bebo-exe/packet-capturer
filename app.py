#!/home/bebo/templates/.venv/bin/python3
"""
Simplified Wireshark-like Browser Packet Analyzer
Real-time packet capture with interface detection
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import logging
import sys
from datetime import datetime
from typing import Dict, List
import socket
import subprocess
import platform
import os
import time
import random

# Ensure scapy is available
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, Ether, ARP, IPv6, get_if_list, conf
    # Import PcapWriter for writing pcap files incrementally
    from scapy.utils import PcapWriter
    print("✓ Scapy imported successfully")
except ImportError as e:
    print(f"✗ ERROR: Scapy not installed: {e}")
    print("Run: pip install scapy")
    sys.exit(1)

# Configure logging
print("[DEBUG] Configuring logging...")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress Flask request logging for cleaner console output
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Create Flask app with explicit template folder
print("[DEBUG] Creating Flask app...")
app = Flask(__name__, template_folder='templates', static_folder='templates')
print("[DEBUG] Flask app created")
# Configure CORS to allow all origins and methods
#CORS(app, resources={
#    r"/api/*": {
#        "origins": "*",
#        "methods": ["GET", "POST", "OPTIONS"],
#        "allow_headers": ["Content-Type"],
#        "supports_credentials": False
#    }
#})
print("[DEBUG] Setting Flask config...")
app.config['JSON_SORT_KEYS'] = False
print("[DEBUG] Flask config set")

# State variables
packets_list = []
is_capturing = False
capture_thread = None

# Capture options and pcap writer
pcap_writer = None
pcap_filename = None

# Configure Scapy for Windows packet capture
# Works with both npcap and winpcap - let Scapy auto-detect
try:
    if platform.system().lower() == 'windows':
        # Enable pcap usage for Windows (npcap/winpcap provides this)
        conf.use_pcap = True
        print("✓ Scapy configured to use npcap/winpcap")
except Exception as e:
    logger.debug(f"Could not configure pcap: {e}")
    print(f"⚠ pcap configuration warning: {e}")

# ============================================================================
# INTERFACE DETECTION & ENHANCEMENT
# ============================================================================

def parse_ipconfig_detailed() -> List[Dict]:
    """Parse adapters on Windows (ipconfig) or Linux (ip -o addr) and return list of adapters

    Keeps the same adapter dict shape used by the rest of the app so callers need no changes.
    """
    adapters = []

    try:
        system = platform.system().lower()

        if 'windows' in system:
            # Original ipconfig parsing for Windows
            result = subprocess.run(
                ['ipconfig', '/all'],
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.split('\n')
            current_adapter = None

            for i, line in enumerate(lines):
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Detect adapter header line (starts with "Ethernet adapter" or "Wireless LAN adapter")
                if line_stripped and not line.startswith(' '):
                    if 'adapter' in line_lower:
                        # Save previous adapter if any
                        if current_adapter:
                            adapters.append(current_adapter)

                        # Determine adapter type from the line
                        is_wireless = 'wireless' in line_lower or 'wi-fi' in line_lower
                        is_loopback = 'loopback' in line_lower

                        # Get adapter name (everything before the colon)
                        adapter_name = line_stripped.split(':')[0].strip() if ':' in line_stripped else line_stripped

                        # Determine type
                        if is_loopback:
                            adapter_type = 'Loopback'
                            display_name = 'Loopback (localhost)'
                            default_ip = '127.0.0.1'
                        elif is_wireless:
                            adapter_type = 'WiFi (Wireless)'
                            display_name = adapter_name.replace('Wireless LAN adapter ', '').strip()
                            default_ip = ''
                        elif 'vmware' in adapter_name.lower():
                            adapter_type = 'Virtual (VMware)'
                            display_name = adapter_name.replace('Ethernet adapter ', '').strip()
                            default_ip = ''
                        else:
                            adapter_type = 'Ethernet'
                            display_name = adapter_name.replace('Ethernet adapter ', '').strip()
                            default_ip = ''

                        current_adapter = {
                            'full_name': adapter_name,
                            'display_name': display_name,
                            'type': adapter_type,
                            'ip': default_ip,
                            'is_wireless': is_wireless,
                            'physical_address': '',
                            'description': ''
                        }

                # Parse adapter details
                elif current_adapter and line.startswith(' ') and ':' in line:
                    key = line.split(':')[0].strip().lower()
                    value = line.split(':', 1)[1].strip() if ':' in line else ''

                    # IPv4 Address
                    if 'ipv4 address' in key:
                        ip = value.split()[0] if value else ''
                        if ip and '.' in ip and '169.254' not in ip:
                            current_adapter['ip'] = ip

                    # Physical Address (MAC)
                    elif 'physical address' in key:
                        current_adapter['physical_address'] = value

                    # Description
                    elif 'description' in key:
                        current_adapter['description'] = value

            # Add last adapter
            if current_adapter:
                adapters.append(current_adapter)

        else:
            # Try a Linux / generic POSIX strategy using `ip -o addr` and `/sys/class/net` for MAC
            try:
                result = subprocess.run(['ip', '-o', 'addr'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.splitlines()

                iface_map = {}
                for line in lines:
                    parts = line.split()
                    # Format: <num>: <iface> <family> <addr> ...
                    if len(parts) >= 4:
                        iface = parts[1]
                        family = parts[2]
                        addr = parts[3]
                        if family == 'inet':
                            ip = addr.split('/')[0]
                            if ip and '.' in ip and not ip.startswith('169.254') and not ip.startswith('127.'):
                                if iface not in iface_map:
                                    iface_map[iface] = {'ip': ip}

                for iface, data in iface_map.items():
                    iface_lower = iface.lower()
                    is_wireless = iface_lower.startswith('wl') or 'wifi' in iface_lower
                    is_loopback = iface_lower == 'lo' or iface_lower.startswith('lo')

                    if is_loopback:
                        adapter_type = 'Loopback'
                        display_name = 'Loopback (localhost)'
                        default_ip = data.get('ip', '127.0.0.1')
                    elif is_wireless:
                        adapter_type = 'WiFi (Wireless)'
                        display_name = iface
                        default_ip = data.get('ip', '')
                    elif iface_lower.startswith(('en', 'eth')):
                        adapter_type = 'Ethernet'
                        display_name = iface
                        default_ip = data.get('ip', '')
                    elif any(x in iface_lower for x in ['tun', 'tap', 'vpn']):
                        adapter_type = 'VPN / Virtual'
                        display_name = iface
                        default_ip = data.get('ip', '')
                    else:
                        adapter_type = 'Network Adapter'
                        display_name = iface
                        default_ip = data.get('ip', '')

                    # Try to read MAC address from sysfs (works on Linux)
                    mac = ''
                    try:
                        with open(f'/sys/class/net/{iface}/address', 'r') as f:
                            mac = f.read().strip()
                    except Exception:
                        try:
                            r2 = subprocess.run(['ip', 'link', 'show', iface], capture_output=True, text=True, timeout=5)
                            out = r2.stdout
                            # Find typical MAC pattern
                            for token in out.split():
                                if token.count(':') >= 5 and len(token) >= 17:
                                    mac = token
                                    break
                        except Exception:
                            mac = ''

                    adapters.append({
                        'full_name': iface,
                        'display_name': display_name,
                        'type': adapter_type,
                        'ip': default_ip,
                        'is_wireless': is_wireless,
                        'physical_address': mac,
                        'description': ''
                    })

            except Exception as e:
                logger.warning(f"Error parsing ip addr output: {e}")

    except Exception as e:
        logger.warning(f"Error parsing ipconfig/ip addr: {e}")

    return adapters


# Build a cache of adapters from ipconfig
_adapter_cache = None
_scapy_interfaces = None

def get_adapter_cache():
    """Get cached adapter list from ipconfig, refresh if needed"""
    global _adapter_cache
    if _adapter_cache is None:
        _adapter_cache = parse_ipconfig_detailed()
    return _adapter_cache


def get_scapy_interfaces() -> Dict[str, str]:
    """Get mapping of friendly names to Scapy interface identifiers"""
    global _scapy_interfaces
    if _scapy_interfaces is None:
        _scapy_interfaces = {}
        try:
            raw_interfaces = get_if_list()
            adapters = get_adapter_cache()
            
            # Build mapping based on adapter types
            ethernet_interfaces = [i for i in raw_interfaces if i]
            wifi_interfaces = []
            loopback_interface = None
            
            for iface in raw_interfaces:
                iface_lower = iface.lower()
                if 'loopback' in iface_lower:
                    loopback_interface = iface
            
            # Assign WiFi to first available interface (after skipping loopback)
            if not loopback_interface and ethernet_interfaces:
                loopback_interface = ethernet_interfaces[0]
                ethernet_interfaces = ethernet_interfaces[1:]
            
            # Map adapters from ipconfig to available Scapy interfaces
            for adapter in adapters:
                if adapter['is_wireless'] and ethernet_interfaces:
                    # Use first available interface for WiFi
                    wifi_iface = ethernet_interfaces.pop(0)
                    _scapy_interfaces[adapter['display_name']] = wifi_iface
                elif 'loopback' in adapter['type'].lower() and loopback_interface:
                    _scapy_interfaces[adapter['display_name']] = loopback_interface
                elif ethernet_interfaces:
                    # Use available interface for Ethernet
                    eth_iface = ethernet_interfaces.pop(0)
                    _scapy_interfaces[adapter['display_name']] = eth_iface
            
            # Fallback: map remaining interfaces
            for iface in raw_interfaces:
                if iface not in _scapy_interfaces.values():
                    iface_lower = iface.lower()
                    if 'loopback' in iface_lower:
                        _scapy_interfaces['Loopback (localhost)'] = iface
                    else:
                        # Assign to first unmapped adapter
                        for adapter in adapters:
                            if adapter['display_name'] not in _scapy_interfaces:
                                _scapy_interfaces[adapter['display_name']] = iface
                                break
        except Exception as e:
            logger.warning(f"Error building Scapy interface mapping: {e}")
    
    return _scapy_interfaces


def get_scapy_interface_for_name(friendly_name: str) -> str:
    """Get the Scapy interface identifier for a friendly adapter name.
    
    SIMPLIFIED for reliability: Removed complex fallback logic that was causing
    wrong interface resolution. Now uses direct type-based matching.
    """
    print(f"[DEBUG] get_scapy_interface_for_name called with: {repr(friendly_name)}")
    
    # Try pre-built mapping first
    mapping = get_scapy_interfaces()
    print(f"[DEBUG] Available mapping keys: {list(mapping.keys())}")
    
    if friendly_name in mapping:
        result = mapping[friendly_name]
        print(f"[DEBUG] Found in mapping: {repr(friendly_name)} -> {repr(result)}")
        return result
    
    # Simple fallback: match by type against adapter cache
    adapters = get_adapter_cache()
    raw_interfaces = get_if_list()
    print(f"[DEBUG] Raw interfaces available: {raw_interfaces}")
    
    # Find the matching adapter
    target_adapter = None
    for adapter in adapters:
        if adapter['display_name'] == friendly_name:
            target_adapter = adapter
            break
    
    if not target_adapter:
        print(f"[DEBUG] Adapter not found in cache, using first non-loopback interface")
        # Fallback to first non-loopback interface
        for iface in raw_interfaces:
            if 'loopback' not in iface.lower():
                print(f"[DEBUG] Using fallback interface: {repr(iface)}")
                return iface
        # Last resort
        if raw_interfaces:
            return raw_interfaces[0]
        return friendly_name
    
    # Match adapter type to Scapy interface
    adapter_type = target_adapter['type'].lower()
    
    # WiFi/Wireless - match wlan*, wifi*, wireless*
    if 'wifi' in adapter_type or 'wireless' in adapter_type:
        for iface in raw_interfaces:
            iface_lower = iface.lower()
            if any(x in iface_lower for x in ['wlan', 'wifi', 'wireless']):
                print(f"[DEBUG] Matched WiFi: {repr(friendly_name)} -> {repr(iface)}")
                return iface
    
    # Loopback - match loopback or 127.x.x.x
    elif 'loopback' in adapter_type:
        for iface in raw_interfaces:
            if 'loopback' in iface.lower():
                print(f"[DEBUG] Matched Loopback: {repr(friendly_name)} -> {repr(iface)}")
                return iface
    
    # Ethernet/Virtual - match eth*, en*, not loopback
    else:
        for iface in raw_interfaces:
            iface_lower = iface.lower()
            if 'loopback' not in iface_lower and any(x in iface_lower for x in ['eth', 'en', 'npf']):
                print(f"[DEBUG] Matched Ethernet/other: {repr(friendly_name)} -> {repr(iface)}")
                return iface
    
    # Final fallback: first non-loopback
    for iface in raw_interfaces:
        if 'loopback' not in iface.lower():
            print(f"[DEBUG] Final fallback: {repr(friendly_name)} -> {repr(iface)}")
            return iface
    
    if raw_interfaces:
        return raw_interfaces[0]
    
    print(f"[DEBUG] WARNING: No interfaces found! Returning friendly_name as-is: {repr(friendly_name)}")
    return friendly_name


def get_interface_info(iface: str) -> Dict:
    """Get detailed information about a network interface"""
    info = {
        'name': iface,
        'friendly_name': iface,
        'ip': '',
        'description': '',
        'type': 'Unknown'
    }
    
    try:
        iface_lower = iface.lower()
        
        # Check cache of ipconfig adapters
        adapters = get_adapter_cache()
        
        # Try to match with ipconfig adapters
        best_match = None
        for adapter in adapters:
            adapter_name_lower = adapter['full_name'].lower()
            display_name = adapter['display_name']
            
            # Direct name match
            if display_name.lower() in iface_lower or iface_lower in display_name.lower():
                best_match = adapter
                break
            
            # Partial matches for common patterns
            if 'wifi' in iface_lower or 'wireless' in iface_lower:
                if adapter['is_wireless'] and not best_match:
                    best_match = adapter
            elif 'loopback' in iface_lower:
                if adapter['type'] == 'Loopback' and not best_match:
                    best_match = adapter
            elif 'vmware' in iface_lower or 'vmnet' in iface_lower:
                if 'vmware' in adapter['full_name'].lower() and not best_match:
                    best_match = adapter
            elif 'ethernet' in iface_lower or 'eth' in iface_lower:
                if 'ethernet' in adapter['full_name'].lower() and 'vmware' not in adapter['full_name'].lower():
                    best_match = adapter
                    break
        
        # If we found a match in ipconfig, use its details
        if best_match:
            info['type'] = best_match['type']
            info['friendly_name'] = best_match['display_name']
            info['ip'] = best_match['ip']
            info['description'] = best_match['description']
        else:
            # Fallback classification based on interface name patterns
            if 'loopback' in iface_lower:
                info['type'] = 'Loopback'
                info['friendly_name'] = 'Loopback (localhost)'
                info['ip'] = '127.0.0.1'
            elif 'wifi' in iface_lower or 'wireless' in iface_lower or 'wlan' in iface_lower:
                info['type'] = 'WiFi (Wireless)'
                info['friendly_name'] = 'WiFi / Wireless Adapter'
            elif 'ethernet' in iface_lower or 'eth' in iface_lower:
                info['type'] = 'Ethernet'
                info['friendly_name'] = 'Ethernet Adapter'
            elif any(x in iface_lower for x in ['vpn', 'tap', 'tun']):
                info['type'] = 'VPN / Virtual'
                info['friendly_name'] = 'VPN / Virtual Adapter'
        
    except Exception as e:
        logger.warning(f"Error getting interface info for {iface}: {e}")
    
    return info


def get_all_interfaces_enhanced() -> List[Dict]:
    """Get list of all network interfaces with detailed info from ipconfig"""
    interfaces = []
    
    try:
        # First priority: get adapters from ipconfig (most reliable for Windows)
        adapters = get_adapter_cache()
        
        # Convert ipconfig adapters to interface list
        if adapters:
            for adapter in adapters:
                interface_dict = {
                    'name': adapter['display_name'],  # Use friendly name as the ID
                    'friendly_name': adapter['display_name'],
                    'ip': adapter['ip'],
                    'description': adapter['description'],
                    'type': adapter['type']
                }
                interfaces.append(interface_dict)
        
        # If no adapters found from ipconfig, fall back to Scapy
        if not interfaces:
            try:
                raw_interfaces = get_if_list()
                
                for iface in raw_interfaces:
                    info = get_interface_info(iface)
                    interfaces.append(info)
            except Exception as e:
                logger.warning(f"Error getting interfaces from Scapy: {e}")
        
        # Remove duplicates (by friendly_name)
        seen_names = set()
        unique_interfaces = []
        for iface in interfaces:
            name = iface['friendly_name']
            if name not in seen_names:
                seen_names.add(name)
                unique_interfaces.append(iface)
        
        interfaces = unique_interfaces
        
        # Sort by type (prefer Ethernet/WiFi over others)
        type_priority = {
            'WiFi (Wireless)': 0,
            'Ethernet': 1,
            'Virtual (VMware)': 2,
            'Network Adapter': 3,
            'VPN / Virtual': 4,
            'Loopback': 5,
            'Unknown': 6
        }
        
        interfaces.sort(key=lambda x: type_priority.get(x['type'], 6))
        
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
    
    return interfaces

# ============================================================================
# ROUTES
# ============================================================================

print("[DEBUG] Registering routes...")

@app.route('/')
def index():
    """Serve main HTML page"""
    return render_template('index.html')

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working!',
        'packets_captured': len(packets_list)
    })

@app.route('/api/interfaces', methods=['GET', 'OPTIONS'])
def get_interfaces():
    """Get network interfaces with detailed information"""
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        logger.info("Fetching network interfaces...")
        interfaces = get_all_interfaces_enhanced()
        
        if not interfaces:
            logger.warning("No network interfaces found")
            return jsonify({
                'success': False,
                'error': 'No network interfaces found. Run with Administrator privileges.',
                'interfaces': [],
                'count': 0
            }), 500
        
        logger.info(f"Successfully found {len(interfaces)} interfaces")
        return jsonify({
            'success': True,
            'interfaces': interfaces,
            'count': len(interfaces),
            'message': f'Found {len(interfaces)} network interface(s)'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get interfaces: {str(e)}',
            'interfaces': [],
            'count': 0
        }), 500

@app.route('/api/start-capture', methods=['POST'])
def start_capture_api():
    """Start packet capture"""
    global is_capturing, capture_thread, packets_list, pcap_writer, pcap_filename, include_arp_icmp

    try:
        data = request.json or {}
        interface = data.get('interface', '').strip()
        count = int(data.get('count', 0)) if data.get('count') is not None else 0
        save_pcap = bool(data.get('save_pcap', False))
        requested_pcap_name = data.get('pcap_filename', '').strip()
        bpf_filter = data.get('filter', '').strip()
        
        # Use default BPF filter if not provided (required for Windows/NPCap)
        if not bpf_filter:
            bpf_filter = 'ip or arp'

        if not interface:
            return jsonify({'success': False, 'error': 'No interface selected'}), 400

        if is_capturing:
            return jsonify({'success': False, 'error': 'Capture already running'}), 400

        # Clear packets and start capturing
        packets_list = []
        is_capturing = True

        # Prepare pcap writer if requested
        pcap_writer = None
        pcap_filename = None
        if save_pcap:
            # Choose filename
            if requested_pcap_name:
                pcap_filename = requested_pcap_name
            else:
                pcap_filename = f"capture_{int(time.time())}.pcap"
            try:
                pcap_writer = PcapWriter(pcap_filename, append=False, sync=True)
                logger.info(f"PCAP writing enabled: {pcap_filename}")
            except Exception as e:
                logger.warning(f"Could not open pcap file for writing: {e}")
                pcap_writer = None
                pcap_filename = None

        # Get interface info for display
        all_ifaces = get_all_interfaces_enhanced()
        iface_info = next((i for i in all_ifaces if i.get('name') == interface), {'name': interface, 'friendly_name': interface})

        # Get the actual Scapy interface to use
        scapy_iface = get_scapy_interface_for_name(interface)

        def capture_packets():
            global is_capturing, pcap_writer
            print(f"[DEBUG] capture_packets() thread started. is_capturing={is_capturing}")
            try:
                logger.info(f"Starting packet capture on {iface_info['friendly_name']} ({scapy_iface}) with filter='{bpf_filter}'")
                print(f"[DEBUG] Beginning sniff on interface: {scapy_iface}")
                print(f"[DEBUG] BPF Filter: {bpf_filter}")
                print(f"[DEBUG] Interface type: {type(scapy_iface)}, Interface value: {repr(scapy_iface)}")

                def packet_callback(pkt):
                    # Process all packet types including ARP and ICMP
                    print(f"[DEBUG] Inside packet_callback, packets_list size before: {len(packets_list)}")
                    try:
                        # Write raw packet to pcap if writer is configured
                        if pcap_writer:
                            try:
                                pcap_writer.write(pkt)
                            except Exception as e:
                                logger.debug(f"Failed to write packet to pcap: {e}")

                        print(f"[DEBUG] Captured packet: {pkt.summary()}")
                        process_packet(pkt)
                        print(f"[DEBUG] After process_packet, packets_list size: {len(packets_list)}")
                    except Exception as e:
                        logger.debug(f"Error in packet_callback: {e}")
                        print(f"[DEBUG] Exception in packet_callback: {e}")

                print("[DEBUG] About to start sniff...")
                # Use single sniff() call with mandatory BPF filter
                # Required for Windows/NPCap to deliver all packet types (TCP, ICMP, DNS, etc)
                # timeout=10 allows time for test traffic to arrive
                
                try:
                    sniff_count = count if count > 0 else 0
                    print(f"[DEBUG] Starting sniff with filter='{bpf_filter}', count={sniff_count}, timeout=10s")
                    sniff(
                        iface=scapy_iface,
                        prn=packet_callback,
                        filter=bpf_filter,
                        store=False,
                        timeout=10  # Wait up to 10 seconds for packets
                    )
                except KeyboardInterrupt:
                    print("[DEBUG] Sniff interrupted by KeyboardInterrupt")
                except Exception as e:
                    print(f"[DEBUG] Sniff exception: {e}")
                    logger.debug(f"Sniff error: {e}")
                
                is_capturing = False
                print(f"[DEBUG] Sniff completed. Total packets: {len(packets_list)}")
            except PermissionError as e:
                logger.error(f"Permission error: {e}")
                logger.error("May need elevated privileges")
                print(f"[DEBUG] PermissionError: {e}")
                is_capturing = False
            except Exception as e:
                logger.error(f"Capture error: {e}")
                print(f"[DEBUG] Capture exception: {e}")
                import traceback
                traceback.print_exc()
                is_capturing = False

        # Start capture in background thread
        capture_thread = threading.Thread(target=capture_packets, daemon=True)
        capture_thread.start()

        return jsonify({
            'success': True,
            'message': f'Capturing on {iface_info["friendly_name"]}',
            'interface': interface,
            'friendly_name': iface_info['friendly_name'],
            'pcap_file': pcap_filename
        })

    except Exception as e:
        logger.error(f"Error in start_capture: {e}")
        is_capturing = False
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop-capture', methods=['POST'])
def stop_capture_api():
    """Stop packet capture"""
    global is_capturing, pcap_writer, pcap_filename
    is_capturing = False

    saved = None
    try:
        if pcap_writer:
            try:
                pcap_writer.close()
                saved = pcap_filename
                logger.info(f"PCAP saved to {pcap_filename}")
            except Exception as e:
                logger.warning(f"Error closing pcap writer: {e}")
            finally:
                pcap_writer = None
                pcap_filename = None
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Capture stopped', 'pcap_file': saved})

@app.route('/api/packets', methods=['GET'])
def get_packets():
    """Get captured packets"""
    try:
        return jsonify({
            'success': True,
            'packets': packets_list,
            'count': len(packets_list),
            'capturing': is_capturing
        })
    except Exception as e:
        logger.error(f"Error getting packets: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'packets': []
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get packet statistics"""
    protocols = {}
    for pkt in packets_list:
        proto = pkt.get('protocol', 'Unknown')
        protocols[proto] = protocols.get(proto, 0) + 1
    
    return jsonify({
        'success': True,
        'total': len(packets_list),
        'protocols': protocols,
        'capturing': is_capturing
    })

@app.route('/api/clear', methods=['POST'])  
def clear_packets():
    """Clear all captured packets"""
    global packets_list
    packets_list = []
    return jsonify({'success': True, 'message': 'Packets cleared'})

# ============================================================================
# PACKET PROCESSING
# ============================================================================

def process_packet(packet):
    """Parse and store packet with enhanced protocol detection and ICMP support"""
    global packets_list
    
    print(f"[DEBUG process_packet] Received packet, packets_list size: {len(packets_list)}, packet summary: {packet.summary()}")

    if len(packets_list) > 1000:
        packets_list.pop(0)  # Remove oldest
    
    pkt_data = {
        'number': len(packets_list) + 1,
        'timestamp': datetime.now().isoformat(),
        'length': len(packet),
        'protocol': 'Other',
        'src_ip': '',
        'dst_ip': '',
        'src_port': '',
        'dst_port': '',
        'info': ''
    }
    
    try:
        # ARP layer (check first, doesn't require IP)
        if packet.haslayer(ARP):
            print("[DEBUG] Found ARP layer")
            arp = packet[ARP]
            pkt_data['protocol'] = 'ARP'
            pkt_data['src_ip'] = arp.psrc
            pkt_data['dst_ip'] = arp.pdst
            pkt_data['info'] = f"{arp.psrc} → {arp.pdst}"
            print(f"[DEBUG] ARP packet stored: {pkt_data['src_ip']} -> {pkt_data['dst_ip']}")
            packets_list.append(pkt_data)
            return
        
        # IP layer
        if packet.haslayer(IP):
            print("[DEBUG] Found IP layer")
            ip = packet[IP]
            pkt_data['src_ip'] = ip.src
            pkt_data['dst_ip'] = ip.dst
            
            # TCP layer
            if packet.haslayer(TCP):
                print("[DEBUG] Found TCP layer")
                tcp = packet[TCP]
                pkt_data['src_port'] = tcp.sport
                pkt_data['dst_port'] = tcp.dport
                
                # Detect HTTPS (port 443)
                if tcp.dport == 443 or tcp.sport == 443:
                    pkt_data['protocol'] = 'HTTPS'
                # Detect HTTP (port 80)
                elif tcp.dport == 80 or tcp.sport == 80:
                    pkt_data['protocol'] = 'HTTP'
                # Generic TCP
                else:
                    pkt_data['protocol'] = 'TCP'
                
                pkt_data['info'] = f":{tcp.sport} → :{tcp.dport}"
                print(f"[DEBUG] TCP packet stored: {pkt_data['protocol']} {pkt_data['src_ip']}:{tcp.sport} -> {pkt_data['dst_ip']}:{tcp.dport}")
            
            # UDP layer
            elif packet.haslayer(UDP):
                print("[DEBUG] Found UDP layer")
                udp = packet[UDP]
                pkt_data['src_port'] = udp.sport
                pkt_data['dst_port'] = udp.dport
                
                # Detect DNS (port 53)
                if udp.dport == 53 or udp.sport == 53:
                    pkt_data['protocol'] = 'DNS'
                # Generic UDP
                else:
                    pkt_data['protocol'] = 'UDP'
                
                pkt_data['info'] = f":{udp.sport} → :{udp.dport}"
                print(f"[DEBUG] UDP packet stored: {pkt_data['protocol']} {pkt_data['src_ip']}:{udp.sport} -> {pkt_data['dst_ip']}:{udp.dport}")
            
            # ICMP layer - Enhanced with type, code, and sequence info
            elif packet.haslayer(ICMP):
                print("[DEBUG] Found ICMP layer")
                icmp = packet[ICMP]
                pkt_data['protocol'] = 'ICMP'
                
                # Extract ICMP type and code
                icmp_type = icmp.type
                icmp_code = icmp.code
                
                # Map ICMP types to human-readable names
                icmp_type_names = {
                    0: 'Echo Reply',
                    3: 'Destination Unreachable',
                    5: 'Redirect',
                    8: 'Echo Request (Ping)',
                    11: 'Time Exceeded',
                    12: 'Parameter Problem',
                    13: 'Timestamp Request',
                    14: 'Timestamp Reply',
                    15: 'Information Request',
                    16: 'Information Reply'
                }
                
                icmp_type_name = icmp_type_names.get(icmp_type, f'Type {icmp_type}')
                
                # Build info string with sequence number if available
                if hasattr(icmp, 'seq'):
                    pkt_data['info'] = f"{icmp_type_name} (Code: {icmp_code}, Seq: {icmp.seq})"
                else:
                    pkt_data['info'] = f"{icmp_type_name} (Code: {icmp_code})"
                print(f"[DEBUG] ICMP packet stored: {pkt_data['info']}")
            
            else:
                pkt_data['protocol'] = 'IP'
                print("[DEBUG] IP packet (no TCP/UDP/ICMP)")
        
        # Ethernet without IP
        elif packet.haslayer(Ether):
            print("[DEBUG] Found Ethernet layer (no IP)")
            pkt_data['protocol'] = 'Ethernet'
    
    except Exception as e:
        logger.debug(f"Error parsing packet: {e}")
        print(f"[DEBUG] Exception in process_packet: {e}")
    
    print(f"[DEBUG] Appending packet: {pkt_data['protocol']}")
    packets_list.append(pkt_data)

# ============================================================================
# RULESET EXPERIMENTS
# ============================================================================


def boyer_moore_search(text: bytes, pattern: bytes) -> bool:
    """Simple Boyer-Moore implementation for bytes (bad-character heuristic)."""
    if not pattern or not text:
        return False
    m, n = len(pattern), len(text)
    if m > n:
        return False
    # Build bad-character skip table
    skip = [m] * 256
    for i in range(m - 1):
        skip[pattern[i]] = m - 1 - i
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            return True
        # advance by skip value for the character aligned with pattern end
        i += skip[text[i + m - 1]] if (i + m - 1) < n else 1
    return False


def kmp_search(text: bytes, pattern: bytes) -> bool:
    """Knuth-Morris-Pratt (used as a stand-in for Aho-Corasick for single-pattern searches)."""
    if not pattern:
        return True
    m, n = len(pattern), len(text)
    if m > n:
        return False
    # Build LPS array
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    # Search
    i = j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return True
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return False


@app.route('/api/run-ruleset', methods=['POST'])
def run_ruleset():
    """Run the example ruleset experiment described in objectives.md.

    Captures N packets, chooses one at random, then runs three search algorithms
    (quick/python 'in', Boyer-Moore, KMP) to locate the pattern in captured packets
    and measures timings.
    """
    data = request.json or {}
    interface = data.get('interface', '').strip()
    count = int(data.get('count', 3000))
    save_pcap = bool(data.get('save_pcap', False))
    requested_pcap_name = data.get('pcap_filename', '').strip()
    bpf_filter = data.get('filter', '').strip()
    
    # Use default BPF filter if not provided (required for Windows/NPCap)
    if not bpf_filter:
        bpf_filter = 'ip or arp'

    if not interface:
        return jsonify({'success': False, 'error': 'No interface specified'}), 400

    scapy_iface = get_scapy_interface_for_name(interface)

    captured = []

    def _cb(pkt):
        captured.append(pkt)

    try:
        sniff(iface=scapy_iface, prn=_cb, filter=bpf_filter, count=count, store=False)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Capture failed: {e}'}), 500

    if not captured:
        return jsonify({'success': False, 'error': 'No packets captured'}), 400

    # Choose random packet as ruleset
    chosen_idx = random.randrange(len(captured))
    pattern_pkt = captured[chosen_idx]
    pattern = bytes(pattern_pkt)

    # Optionally save captured pcap
    saved_pcap = None
    if save_pcap:
        try:
            writer = PcapWriter(requested_pcap_name or f"ruleset_capture_{int(time.time())}.pcap", append=False, sync=True)
            for p in captured:
                writer.write(p)
            writer.close()
            saved_pcap = requested_pcap_name or f"ruleset_capture_{int(time.time())}.pcap"
        except Exception as e:
            logger.warning(f"Failed to save ruleset pcap: {e}")

    # Prepare bytes list
    bytes_list = [bytes(p) for p in captured]

    results = {}

    # Quick (python 'in')
    start = time.perf_counter()
    quick_matches = sum(1 for b in bytes_list if pattern in b)
    t_quick = time.perf_counter() - start
    results['quick'] = {'matches': quick_matches, 'time_s': t_quick}

    # Boyer-Moore
    start = time.perf_counter()
    bm_matches = sum(1 for b in bytes_list if boyer_moore_search(b, pattern))
    t_bm = time.perf_counter() - start
    results['boyer_moore'] = {'matches': bm_matches, 'time_s': t_bm}

    # KMP (as Aho substitute)
    start = time.perf_counter()
    kmp_matches = sum(1 for b in bytes_list if kmp_search(b, pattern))
    t_kmp = time.perf_counter() - start
    results['kmp'] = {'matches': kmp_matches, 'time_s': t_kmp}

    return jsonify({
        'success': True,
        'chosen_index': chosen_idx,
        'chosen_summary': pattern_pkt.summary(),
        'pattern_len': len(pattern),
        'results': results,
        'saved_pcap': saved_pcap,
        'expected_complexities': {
            'quick': 'Depends on implementation (Python uses optimized search)',
            'boyer_moore': 'Average sublinear, worst-case O(n*m)',
            'kmp': 'O(n + m)'
        }
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  WIRESHARK WEB - PACKET ANALYZER")
    print("="*70)
    
    # Verify npcap installation on Windows
    if platform.system().lower() == 'windows':
        print("\n🔍 Checking npcap installation...")
        npcap_installed = False
        npcap_paths = [
            r"C:\Windows\System32\npcap\wpcap.dll",
            r"C:\Program Files\npcap\wpcap.dll",
            r"C:\Program Files (x86)\npcap\wpcap.dll",
        ]
        
        for dll_path in npcap_paths:
            if os.path.exists(dll_path):
                print(f"✓ npcap found at: {dll_path}")
                npcap_installed = True
                break
        
        if not npcap_installed:
            print("✗ ERROR: npcap is not installed!")
            print("\n📥 To install npcap:")
            print("   1. Download from: https://nmap.org/npcap/")
            print("   2. Run the installer (npcap-1.x.x.exe)")
            print("   3. Choose 'Install npcap in WinPcap API-compatible mode' during installation")
            print("   4. Restart this application")
            print("\n⚠️  Packet capture will not work without npcap!")
    
    # Check interfaces
    try:
        ifaces = get_if_list()
        print(f"\n✓ Found {len(ifaces)} network interface(s)")
        if len(ifaces) > 0:
            print(f"  First interface: {ifaces[0]}")
    except Exception as e:
        print(f"\n⚠ Could not detect interfaces: {e}")
    
    print("\n📡 Starting Flask server...")
    print("   URL: http://localhost:5000")
    print("   API: http://localhost:5000/api/test")
    print("\n💡 TIPS:")
    print("   - Press CTRL+C to stop")
    print("   - Must run as Administrator (Windows) or with sudo (Linux)")
    print("   - Open browser to http://localhost:5000")
    print("="*70 + "\n")
    
    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
