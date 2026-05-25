import sys
from genie.testbed import load

def test_network():
    testbed = load('pyats/testbed.yaml')
    device = testbed.devices['srl1']
    
    print(f"Opening automation connection to {device.name} via secure tunnel...")
    device.connect(log_stdout=False)
    
    output = device.parse('show version')
    print("\n==============================")
    print("      NOKIA STATE REPORT      ")
    print("==============================")
    print(f"OS Version Identified: {output.get('version', 'Unknown')}")
    print("==============================\n")
    
    device.disconnect()

if __name__ == "__main__":
    test_network()
