import sys
import json
import requests
from genie.testbed import load

def deploy_config_via_jsonrpc(tunnel_ip, tunnel_port):
    """Pushes configurations to Nokia SR Linux using its built-in JSON-RPC server"""
    url = f"https://{tunnel_ip}:{tunnel_port}/jsonrpc"
    headers = {"Content-Type": "application/json"}
    
    # Load our structured configuration file
    with open("config/srl_interfaces.json", "r") as f:
        config_data = json.load(f)
        
    # Construct the native Nokia JSON-RPC edit request
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "set",
        "params": {
            "commands": [
                {
                    "action": "update",
                    "path": "/interface",
                    "value": config_data["interface"]
                }
            ]
        }
    }
    
    print("🤖 Sending configuration payload via JSON-RPC tunnel...")
    # verify=False is used because the container uses a self-signed SSL cert
    response = requests.post(url, auth=("admin", "admin"), json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print("✅ Configuration applied successfully!")
    else:
        print(f"❌ Configuration failed: {response.text}")
        sys.exit(1)

def verify_network_state():
    """Uses pyATS to connect via SSH and verify the interface state"""
    testbed = load('pyats/testbed.yaml')
    device = testbed.devices['srl1']
    
    print(f"🔌 Connecting to {device.name} via SSH proxy to verify state...")
    device.connect(log_stdout=False)
    
    # Execute a show command to verify the interface state
    print("📊 Extracting running interface states...")
    output = device.execute("show interface loopback0")
    print(output)
    
    # Simple programmatic validation check
    if "up" in output.lower() and "192.168.100.1" in output:
        print("\n🎉 VALIDATION SUCCESS: loopback0 is up and bound to 192.168.100.1/32!")
    else:
        print("\n🚨 VALIDATION FAILED: Interface configuration not found or interface down!")
        sys.exit(1)
        
    device.disconnect()

if __name__ == "__main__":
    # Extract the dynamic tunnel parameters directly from your testbed file
    tb = load('pyats/testbed.yaml')
    dev = tb.devices['srl1']
    host = dev.connections['cli']['ip']
    
    # Map the secure web port (Since our pinggy tunnel maps port 22, 
    # we use the mapped SSH port directly for management connectivity verification)
    deploy_config_via_jsonrpc(host, dev.connections['cli']['port'])
    verify_network_state()
