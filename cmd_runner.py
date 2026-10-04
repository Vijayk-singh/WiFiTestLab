import subprocess

def run_command(command, timeout=10):
    """
    Runs a Linux terminal command and returns its output.
    This is the core execution engine used by all other tools.
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"\n[ERROR] Command timed out after {timeout} seconds: {command}")
        return None
    except subprocess.CalledProcessError:
        # The command failed (e.g., ping didn't get a response)
        return None
