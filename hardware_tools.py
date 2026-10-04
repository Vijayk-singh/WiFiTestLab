import re
from cmd_runner import run_command

"""
HARDWARE & SECURITY TOOLS
This module handles the physical layer diagnostics and security validation.
"""

def get_default_interface():
    output = run_command("ip route | grep default")
    if output:
        parts = output.split()
        if "dev" in parts:
            return parts[parts.index("dev") + 1]
    return None

def is_interface_up(interface):
    if not interface: return False
    output = run_command(f"ip link show {interface}")
    return output and "state UP" in output

def get_connected_ssid(interface):
    if not interface: return None
    return run_command(f"iwgetid {interface} -r")

def get_wifi_security_type(interface):
    """
    Checks the security encryption (WPA2/WPA3/Open) of the connected Wi-Fi.
    [RESUME ALIGNMENT]: "Defensive Wi-Fi security validation checks"
    """
    if not interface: return None
    # nmcli is standard on most modern Linux distros (Ubuntu/Fedora)
    # Using --rescan no so the command executes instantly and doesn't timeout
    output = run_command(r"nmcli -t -f IN-USE,SECURITY dev wifi list --rescan no | grep '^\*'")
    if output:
        # Example output: "*:WPA2 WPA3"
        parts = output.split(':')
        if len(parts) > 1:
            return parts[1]
    return "Unknown (nmcli not available)"

def detect_rogue_ap(interface, ssid):
    """
    Scans for Rogue Access Points (Evil Twins).
    Alerts if multiple BSSIDs broadcast the same SSID with mismatched security.
    """
    if not interface or not ssid: 
        return {"rogue_detected": False, "reason": "No SSID provided"}
    
    # Get a list of all visible networks
    output = run_command("nmcli -f SSID,BSSID,SECURITY dev wifi list")
    if not output: 
        return {"rogue_detected": False, "reason": "Could not scan networks"}
    
    matching_aps = []
    for line in output.split('\n'):
        # Match the exact SSID in the line
        if ssid in line:
            matching_aps.append(line.strip())
            
    if len(matching_aps) > 1:
        # If there are multiple APs with the same name, check their security
        security_types = set()
        for ap in matching_aps:
            # Simple check if the AP line contains secure keywords
            if "WPA" in ap or "WEP" in ap or "802.1X" in ap:
                security_types.add("Secure")
            else:
                security_types.add("Open")
                
        if len(security_types) > 1:
            return {"rogue_detected": True, "reason": f"CRITICAL: Found multiple APs for '{ssid}' with mismatched security. Possible Evil Twin!"}
        else:
            return {"rogue_detected": False, "reason": f"Multiple APs for '{ssid}' detected (Likely a Mesh network/Extender)."}
            
    return {"rogue_detected": False, "reason": "Only one AP detected for this SSID."}

def get_wifi_metrics(interface):
    """Extracts hardware-level Wi-Fi metrics (Signal Strength)."""
    if not interface: return None
    output = run_command(f"iwconfig {interface}")
    if output:
        quality_match = re.search(r'Link Quality=(\d+/\d+)', output)
        signal_match = re.search(r'Signal level=(-\d+) dBm', output)
        return {
            "link_quality": quality_match.group(1) if quality_match else None,
            "signal_level_dbm": int(signal_match.group(1)) if signal_match else None
        }
    return None
