import re
import os
from cmd_runner import run_command

"""
NETWORK TOOLS
This module handles the routing layer diagnostics and packet analysis.
"""

def get_ip_address(interface):
    if not interface: return None
    output = run_command(f"ip addr show {interface}")
    if output:
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
    return None

def get_gateway_ip():
    output = run_command("ip route | grep default")
    if output:
        match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
    return None

def ping_host(host, count=4):
    """Parses ping output to extract Packet Loss and Average Latency."""
    if not host: 
        return {"success": False, "packet_loss_pct": 100, "avg_latency_ms": None}
        
    output = run_command(f"ping -c {count} {host}")
    if not output:
        return {"success": False, "packet_loss_pct": 100, "avg_latency_ms": None}
        
    loss_match = re.search(r'(\d+)% packet loss', output)
    packet_loss = int(loss_match.group(1)) if loss_match else 100
    
    avg_latency = None
    time_match = re.search(r'=\s+[\d\.]+/([\d\.]+)/', output)
    if time_match:
        avg_latency = float(time_match.group(1))
        
    return {
        "success": packet_loss < 100,
        "packet_loss_pct": packet_loss,
        "avg_latency_ms": avg_latency
    }

def capture_diagnostic_packets(interface, duration_sec=3, filename="evidence.pcap"):
    """
    Captures network traffic for diagnostic evidence if a test fails.
    [RESUME ALIGNMENT]: "Diagnostic evidence collection using tcpdump/tshark"
    """
    if not interface: return False
    
    print(f"\n[DIAGNOSTIC] Capturing {duration_sec}s of packet data to {filename}...")
    # 'timeout' command automatically kills tcpdump after duration_sec.
    # Note: Requires 'sudo' privileges to actually capture in the real world.
    run_command(f"sudo timeout {duration_sec} tcpdump -i {interface} -w {filename}", timeout=duration_sec + 2)
    
    return os.path.exists(filename)
