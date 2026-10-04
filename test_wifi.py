import pytest
import hardware_tools
import network_tools

# Get the network interface once at the module level
INTERFACE = hardware_tools.get_default_interface()

# [RESUME ALIGNMENT]: "Configurable Thresholds"
THRESHOLDS = {
    "min_signal_dbm": -80,
    "max_local_latency_ms": 50,
    "max_internet_loss_pct": 25,
    "max_internet_latency_ms": 200
}

class TestWiFiHardware:
    """Tests focusing on the physical network interface and security."""
    
    def test_interface_exists(self):
        assert INTERFACE is not None, "No default network interface found."
        print(f"\n[INFO] Primary Interface: {INTERFACE}")

    def test_interface_is_up(self):
        assert hardware_tools.is_interface_up(INTERFACE), f"Interface {INTERFACE} is down!"

    def test_wifi_security_configuration(self):
        """
        [RESUME ALIGNMENT]: "Defensive Wi-Fi security validation checks"
        Ensures the network is not Open and is using modern encryption (WPA2/WPA3).
        """
        if not INTERFACE.startswith(('wl', 'wlan')):
            pytest.skip("Not a wireless interface.")
            
        security = hardware_tools.get_wifi_security_type(INTERFACE)
        print(f"\n[INFO] Wi-Fi Security Encryption: {security}")
        assert "WPA" in security, f"Security vulnerability: Connected to insecure network ({security})"

    def test_rogue_ap_detection(self):
        """
        [RESUME ALIGNMENT]: "Defensive Wi-Fi security validation"
        Scans for Evil Twin attacks (Rogue APs spoofing your network).
        """
        if not INTERFACE.startswith(('wl', 'wlan')):
            pytest.skip("Not a wireless interface.")
            
        ssid = hardware_tools.get_connected_ssid(INTERFACE)
        if not ssid:
            pytest.skip("Not connected to Wi-Fi.")
            
        rogue_check = hardware_tools.detect_rogue_ap(INTERFACE, ssid)
        print(f"\n[INFO] Rogue AP Check: {rogue_check['reason']}")
        assert rogue_check['rogue_detected'] == False, f"SECURITY ALERT: {rogue_check['reason']}"

    def test_wifi_signal_strength(self):
        if not INTERFACE.startswith(('wl', 'wlan')):
            pytest.skip("Not a wireless interface.")
            
        metrics = hardware_tools.get_wifi_metrics(INTERFACE)
        if metrics and metrics.get('signal_level_dbm'):
            signal = metrics['signal_level_dbm']
            print(f"\n[INFO] Signal Level: {signal} dBm")
            assert signal >= THRESHOLDS["min_signal_dbm"], f"Signal too weak: {signal} dBm"


class TestLocalNetwork:
    """Tests focusing on local routing and IP assignment."""
    
    def test_dhcp_ip_assignment(self):
        ip = network_tools.get_ip_address(INTERFACE)
        assert ip is not None, f"No IP address found for {INTERFACE}."
        print(f"\n[INFO] Assigned IP Address: {ip}")

    def test_gateway_connectivity_and_latency(self):
        """[RESUME ALIGNMENT]: "Repeatable network checks for latency, packet loss" """
        gateway_ip = network_tools.get_gateway_ip()
        assert gateway_ip is not None, "Could not find router (gateway) IP."
        
        ping_stats = network_tools.ping_host(gateway_ip, count=4)
        assert ping_stats["success"], f"Failed to ping router at {gateway_ip}."
        assert ping_stats["packet_loss_pct"] == 0, f"Local packet loss: {ping_stats['packet_loss_pct']}%"
        
        if ping_stats["avg_latency_ms"]:
            latency = ping_stats["avg_latency_ms"]
            assert latency < THRESHOLDS["max_local_latency_ms"], f"High local latency: {latency}ms"


class TestInternetConnectivity:
    """Tests focusing on external access and DNS resolution."""
    
    def test_public_dns_reachability(self):
        ping_stats = network_tools.ping_host("8.8.8.8", count=4)
        
        # [RESUME ALIGNMENT]: "Diagnostic evidence collection... to correlate failed tests"
        if not ping_stats["success"]:
            print("\n[FAULT DOMAIN] Local network is fine, but Internet is unreachable. Triggering packet capture...")
            network_tools.capture_diagnostic_packets(INTERFACE)
            pytest.fail("Internet (8.8.8.8) is unreachable. Packet capture saved.")
            
        print(f"\n[INFO] Internet Latency (8.8.8.8): {ping_stats['avg_latency_ms']}ms")

    def test_dns_resolution_and_latency(self):
        """[RESUME ALIGNMENT]: "DNS response time... and connectivity reliability" """
        ping_stats = network_tools.ping_host("apple.com", count=4)
        assert ping_stats["success"], "DNS resolution failed or apple.com is unreachable."
        
        loss = ping_stats["packet_loss_pct"]
        latency = ping_stats["avg_latency_ms"]
        
        assert loss <= THRESHOLDS["max_internet_loss_pct"], f"High internet packet loss: {loss}%"
        if latency:
            assert latency < THRESHOLDS["max_internet_latency_ms"], f"High internet latency: {latency}ms"
