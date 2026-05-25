import sys
import time
import paramiko
from genie.testbed import load

def execute_automation_pipeline():
    # Load dynamic tunnel properties
    testbed = load('pyats/testbed.yaml')
    device = testbed.devices['srl1']
    host = device.connections['cli']['ip']
    port = device.connections['cli']['port']
    
    print(f"🔌 Initializing secure SSH tunnel directly to {host}:{port}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Establish connection with explicit timeouts
        ssh.connect(hostname=host, port=int(port), username="admin", password="admin", timeout=10)
        channel = ssh.invoke_shell()
        time.sleep(1)
        
        print("🤖 Injecting candidate datastore loopback changes...")
        # Send clean line executions with trailing carriage returns
        channel.send("enter candidate\n")
        time.sleep(0.5)
        channel.send("interface loopback0 description Automation-SSH-Loopback admin-state enable subinterface 0 ipv4 address 192.168.100.1/32 admin-state enable\n")
        time.sleep(0.5)
        channel.send("commit stay\n")
        time.sleep(0.5)
        channel.send("show interface loopback0\n")
        time.sleep(1.5)
        
        # Pull execution logs from buffer
        output = channel.recv(65535).decode('utf-8')
        print("\n=== RUNTIME LAYER BUFFER OUTPUT ===")
        print(output)
        print("====================================\n")
        
        ssh.close()
        
        # State Assertion Evaluation
        if "192.168.100.1" in output:
            print("🎉 NetDevOps VALIDATION SUCCESS: loopback0 is running live!")
            sys.exit(0)
        else:
            print("❌ NetDevOps VALIDATION FAILED: Interface signature not captured in string buffer.")
            sys.exit(1)
            
    except Exception as e:
        print(f"🚨 Network Execution Engine Crash: {e}")
        sys.exit(1)

if __name__ == "__main__":
    execute_automation_pipeline()
