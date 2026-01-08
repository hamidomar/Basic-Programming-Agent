import asyncio
import paramiko
from typing import Dict, Any

class VMExecutor:
    """Manages VM for Python code execution via SSH"""
    
    def __init__(self, vm_ip: str, username: str):
        self.vm_ip = vm_ip
        self.username = username
        self.ssh = None
    
    async def start(self):
        """Initialize SSH connection"""
        print(f"\n🚀 Connecting to VM {self.vm_ip}...")
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect (uses gcloud compute ssh internally for auth)
        await asyncio.to_thread(
            self.ssh.connect,
            hostname=self.vm_ip,
            username=self.username
        )
        print(f"✓ VM connection ready\n")
    
    async def execute(self, code: str) -> Dict[str, Any]:
        """Execute Python code on VM - SAME SIGNATURE as E2B"""
        if not self.ssh:
            return {
                "success": False,
                "error": "VM not connected. Call start() first."
            }
        
        try:
            # Execute python with code as string (Sub-approach A)
            cmd = f"python3 -c {repr(code)}"
            
            stdin, stdout, stderr = await asyncio.to_thread(
                self.ssh.exec_command, cmd
            )
            
            output = stdout.read().decode()
            errors = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                "success": exit_code == 0,
                "output": output,
                "stderr": errors,
                "error": None if exit_code == 0 else errors,
                "results": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}"
            }
    
    async def stop(self):
        """Close SSH connection"""
        if self.ssh:
            self.ssh.close()
            print("\n✓ VM connection closed")