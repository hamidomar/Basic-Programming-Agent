"""
E2B Code Execution Wrapper
"""
import asyncio
from typing import Dict, Any
from e2b_code_interpreter import AsyncSandbox


class CodeExecutor:
    """Manages E2B sandbox for secure Python code execution"""
    
    def __init__(self):
        self.sandbox = None
    
    async def start(self):
        """Initialize the E2B sandbox"""
        print("\n🚀 Starting E2B sandbox...")
        self.sandbox = await AsyncSandbox.create()
        print(f"✓ Sandbox ready: {self.sandbox.id}\n")
    
    async def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in the sandbox
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with success status, output, and errors
        """
        if not self.sandbox:
            return {
                "success": False,
                "error": "Sandbox not initialized. Call start() first."
            }
        
        try:
            execution = await self.sandbox.run_code(code)
            
            return {
                "success": True,
                "output": execution.logs.stdout,
                "stderr": execution.logs.stderr,
                "error": execution.error,
                "results": execution.results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}"
            }
    
    async def install_package(self, package: str) -> Dict[str, Any]:
        """
        Install a Python package in the sandbox
        
        Args:
            package: Package name (e.g., 'numpy', 'pandas==2.0.0')
            
        Returns:
            Dictionary with success status and output
        """
        if not self.sandbox:
            return {
                "success": False,
                "error": "Sandbox not initialized"
            }
        
        try:
            print(f"📦 Installing {package}...")
            process = await self.sandbox.commands.run(f"pip install {package}")
            
            return {
                "success": process.exit_code == 0,
                "output": process.stdout,
                "error": process.stderr if process.exit_code != 0 else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop(self):
        """Clean up and close the sandbox"""
        if self.sandbox:
            await self.sandbox.close()
            print("\n✓ Sandbox closed")