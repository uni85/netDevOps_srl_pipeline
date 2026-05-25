import sys
import time
import paramiko

def test_local_container():
    print(" Testing isolated local SSH pipeline on 127.0.0.1:2223...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname="127.0.0.1", port=2223, username="admin", password="admin", timeout=5)
        channel = ssh.invoke_shell()
        time.sleep(1)
        
        print(" Local SSH Pipeline Connected! Verifying channel execution...")
        channel.send("whoami\n")
        time.sleep(1)
        
        output = channel.recv(65535).decode('utf-8')
        print("\n=== SYSTEM OUTPUT ===")
        print(output)
        print("======================\n")
        ssh.close()
        print(" local_verify.py PASSED NATIVELY!")
        
    except Exception as e:
        print(f" Local Connection Failed: {e}")

if __name__ == "__main__":
    test_local_container()
