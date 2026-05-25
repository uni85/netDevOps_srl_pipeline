import sys
import paramiko
from genie.testbed import load

def test_via_paramiko_fallback(host, port):
    """Fallback execution path using standard SSH raw channels"""
    print("🔄 Initializing raw SSH fallback channel...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname=host, port=int(port), username="admin", password="admin", timeout=15)
        
        # Open an interactive shell session
        channel = ssh.invoke_shell()
        channel.send("enter candidate\n")
        channel.send("interface loopback0 description Automation-SSH-Loopback admin-state enable subinterface 0 ipv4 address 192.168.100.1/32 admin-state enable\n")
        channel.send("commit stay\n")
        channel.send("show interface loopback0\n")
        
        # Read the terminal execution buffer output
        import time
        time.sleep(3)
        output = channel.recv(10000).decode('utf-8')
        print(output)
        
        if "192.168.100.1" in output:
            print("\n🎉 NetDevOps VALIDATION SUCCESS via SSH Channel!")
            ssh.close()
            return True
    except Exception as e:
        print(f"❌ Handshake failed: {e}")
    
    if ssh:
        ssh.close()
    return False

def automate_nokia_via_pyats():
    testbed = load('pyats/testbed.yaml')
    device = testbed.devices['srl1']
    host = device.connections['cli']['ip']
    port = device.connections['cli']['port']
    
    print(f"🔌 Establishing tunnel SSH connection to {device.name}...")
    try:
        # Lower timeout value to fail fast and trigger the fallback if it hangs
        device.connect(log_stdout=True, connection_timeout=15)
        
        print("🤖 Injecting configurations via native pyATS framework...")
        device.execute("enter candidate")
        device.execute("interface loopback0 description Automation-SSH-Loopback admin-state enable subinterface 0 ipv4 address 192.168.100.1/32 admin-state enable")
        device.execute("commit stay")
        
        state_output = device.execute("show interface loopback0")
        if "192.168.100.1" in state_output:
            print("\n🎉 NetDevOps VALIDATION SUCCESS via pyATS!")
            device.disconnect()
            return
            
    except Exception as pyats_error:
        print(f"⚠️ pyATS connection driver timed out: {pyats_error}")
        
        # Execute fallback option
        success = test_via_paramiko_fallback(host, port)
        if success:
            sys.exit(0)
        else:
            print("\n🚨 NetDevOps VALIDATION FAILED: Both automation drivers failed to execute.")
            sys.exit(1)

if __name__ == "__main__":
    automate_nokia_via_pyats()
