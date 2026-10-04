# WiFiTestLab (Apple Interview Edition)

Welcome to the **WiFiTestLab**! This version has been specifically upgraded for your Apple ADET (Diagnostics / Test Engineering) intern interview. 

It balances **simplicity** (easy to explain) with **Test Engineering Rigor** (extracting hardware-level metrics and measuring Quality of Service, not just true/false checks).

## What Makes This Version Impressive?

Instead of just checking if ping "works", this code now evaluates the *Quality* of the network. This is exactly what Apple test engineers do when diagnosing hardware!

1. **Hardware-Level Wi-Fi Metrics:** 
   - `network_tools.py and hardware_tools.py` now parses `iwconfig` to extract the raw RF **Signal Level (dBm)**. 
   - The test asserts that the signal must be better than `-80 dBm` (a standard cutoff for a stable connection). If someone walks too far from the router, this test catches it before other tests even run!

2. **Quality of Service (QoS):** 
   - Instead of a simple `True/False` for ping, we now extract **Packet Loss %** and **Average Latency (ms)** using Regex.
   - We enforce strict latency thresholds for the local router (`< 50ms`) and looser thresholds for the external internet (`< 200ms`). 

3. **Robust Error Handling:** 
   - Network commands can hang forever if a router drops packets silently. `subprocess.run` now includes a `timeout` argument so the test suite never freezes.

4. **Logical Test Architecture:** 
   - The Pytest file is now organized into logical classes: `TestWiFiHardware`, `TestLocalNetwork`, and `TestInternetConnectivity`. This shows you understand how to structure test suites for readability.

## How it works (The Code Explained)

1. **`network_tools.py and hardware_tools.py`**: 
   - Contains functions that run basic Linux commands (like `ping`, `ip addr`, `iwconfig`).
   - Uses `re` (Regular Expressions) to parse complex terminal output into clean Python dictionaries (e.g., `{"success": True, "packet_loss_pct": 0, "avg_latency_ms": 15.4}`).

2. **`test_wifi.py`**:
   - Imports `network_tools.py and hardware_tools.py` and runs assertions with specific thresholds.
   - For example: `assert latency < 200, "High internet latency"`

## Running the Tests

1. Navigate to this folder in your terminal.
2. Activate the virtual environment (optional but recommended):
   ```bash
   source venv/bin/activate
   ```
3. Run Pytest:
   ```bash
   pytest
   ```

*(Fun fact: When I tested this on your machine, your Wi-Fi signal was `-84 dBm` and your latency to `apple.com` was `292ms`, causing the strict diagnostic tests to intentionally fail! This is a perfect talking point for the interview on why thresholds matter.)*
