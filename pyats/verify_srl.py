import sys
from genie.testbed import load

def automate_nokia_via_ssh():
    # Load your topology map parameters
    testbed = load('pyats/testbed.yaml')
    device = testbed.devices['srl1']
    
    print(f"🔌 Establishing secure tunnel SSH connection to {device.name}...")
    device.connect(log_stdout=True)
    
    # Step 1: Programmatically enter configuration mode and deploy interface changes
    print("🤖 Injecting Loopback0 interface state configuration via SSH...")
    config_commands = [
        "enter candidate",
        "interface loopback0 description Automation-SSH-Loopback admin-state enable subinterface 0 ipv4 address 192.168.100.1/32 admin-state enable",
        "commit stay"
    ]
    
    for cmd in config_commands:
        device.execute(cmd)
    
    print("✅ Configuration committed into Nokia running datastore successfully.")
    
    # Step 2: Extract real-time operational state to assert success
    print("📊 Executing state validation assertions...")
    state_output = device.execute("show interface loopback0")
    
    # Python State Assertion validation check
    if "up" in state_output.lower() and "192.168.100.1" in state_output:
        print("\n🎉 NetDevOps VALIDATION SUCCESS: loopback0 is up and bound to 192.168.100.1/32!")
    else:
        print("\n🚨 NetDevOps VALIDATION FAILED: Interface operational state check failed!")
        sys.exit(1)
        
    device.disconnect()

if __name__ == "__main__":
    automate_nokia_via_ssh()
