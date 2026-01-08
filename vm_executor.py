"""
VM Code Execution Wrapper using gcloud SSH
"""
import asyncio
import shlex
from typing import Dict, Any


class VMExecutor:
    """Manages VM for Python code execution via gcloud SSH tunnel"""
    
    def __init__(self, vm_ip: str, username: str, vm_name: str = None, zone: str = "us-central1-a"):
        self.vm_ip = vm_ip  # Not used in gcloud method, but kept for compatibility
        self.username = username
        self.vm_name = vm_name or "agent-exec-instance"
        self.zone = zone
        self.project = "beciren-advncanlytc-9595"
    
    async def start(self):
        """Verify gcloud SSH connection to VM"""
        print(f"\nConnecting to VM via gcloud SSH tunnel...")
        print(f"  VM: {self.vm_name}")
        print(f"  Zone: {self.zone}")
        print(f"  User: {self.username}")
        
        # Test connection with simple echo command
        cmd = [
            "gcloud", "compute", "ssh",
            f"{self.username}@{self.vm_name}",
            f"--zone={self.zone}",
            f"--project={self.project}",
            "--command=echo 'Connection test successful'"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print(f"VM connection ready\n")
            else:
                error_msg = stderr.decode().strip()
                raise Exception(f"Failed to connect to VM: {error_msg}")
        
        except FileNotFoundError:
            raise Exception(
                "gcloud CLI not found. Please install it from:\n"
                "https://cloud.google.com/sdk/docs/install"
            )
        except Exception as e:
            raise Exception(f"Connection failed: {str(e)}")
    
    async def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code on VM via gcloud SSH
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with success status, output, and errors
        """
        # Escape code for shell - use shlex.quote for safety
        code_escaped = shlex.quote(code)
        
        # Build gcloud command
        cmd = [
            "gcloud", "compute", "ssh",
            f"{self.username}@{self.vm_name}",
            f"--zone={self.zone}",
            f"--project={self.project}",
            f"--command=python3 -c {code_escaped}"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode()
            errors = stderr.decode()
            
            # Filter out gcloud SSH connection noise from stderr
            # gcloud sometimes outputs connection info to stderr
            error_lines = [
                line for line in errors.split('\n')
                if line.strip() and not any(noise in line.lower() for noise in [
                    'updating project ssh metadata',
                    'waiting for ssh key to propagate',
                    'warning: permanently added',
                    'external ip address was not found'
                ])
            ]
            clean_errors = '\n'.join(error_lines)
            
            return {
                "success": process.returncode == 0,
                "output": output,
                "stderr": clean_errors,
                "error": None if process.returncode == 0 else clean_errors,
                "results": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "stderr": ""
            }
    
    async def stop(self):
        """Close connection (no persistent connection with gcloud)"""
        print("\nVM connection closed")