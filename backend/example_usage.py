"""
Example Usage Script
Demonstrates how to interact with the Backend API using Python requests
"""

import requests
import json
import time
from typing import Dict, Any


class BackendAPIClient:
    """
    Client for interacting with the Backend API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def _print_response(self, title: str, response: requests.Response):
        """Pretty print API response"""
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
        
        print("="*60)
    
    # System Endpoints
    def get_system_info(self):
        """Get system information"""
        response = self.session.get(f"{self.base_url}/system/info")
        self._print_response("SYSTEM INFO", response)
        return response.json()
    
    def get_system_status(self):
        """Get system status"""
        response = self.session.get(f"{self.base_url}/system/status")
        self._print_response("SYSTEM STATUS", response)
        return response.json()
    
    def get_layers(self):
        """Get OS layers information"""
        response = self.session.get(f"{self.base_url}/system/layers")
        self._print_response("OS LAYERS", response)
        return response.json()
    
    def get_commands(self):
        """Get all available commands"""
        response = self.session.get(f"{self.base_url}/system/commands")
        self._print_response("AVAILABLE COMMANDS", response)
        return response.json()
    
    def get_uptime(self):
        """Get system uptime"""
        response = self.session.get(f"{self.base_url}/system/uptime")
        self._print_response("SYSTEM UPTIME", response)
        return response.json()
    
    def reload_system(self):
        """Trigger system reload"""
        response = self.session.post(f"{self.base_url}/system/reload")
        self._print_response("SYSTEM RELOAD", response)
        return response.json()
    
    # Shell Endpoints
    def execute_command(self, command: str, args: list = None):
        """Execute a shell command"""
        payload = {
            "command": command,
            "args": args or []
        }
        response = self.session.post(f"{self.base_url}/shell/execute", json=payload)
        self._print_response(f"EXECUTE: {command}", response)
        return response.json()
    
    def list_shell_commands(self):
        """List available shell commands"""
        response = self.session.get(f"{self.base_url}/shell/commands")
        self._print_response("SHELL COMMANDS", response)
        return response.json()
    
    def get_command_info(self, command_name: str):
        """Get info about a specific command"""
        response = self.session.get(f"{self.base_url}/shell/command/{command_name}")
        self._print_response(f"COMMAND INFO: {command_name}", response)
        return response.json()
    
    def execute_batch(self, commands: list):
        """Execute multiple commands"""
        payload = [{"command": cmd} for cmd in commands]
        response = self.session.post(f"{self.base_url}/shell/batch", json=payload)
        self._print_response("BATCH EXECUTION", response)
        return response.json()
    
    # File Endpoints
    def list_files(self, path: str = "/"):
        """List files in directory"""
        response = self.session.get(f"{self.base_url}/files/list", params={"path": path})
        self._print_response(f"LIST FILES: {path}", response)
        return response.json()
    
    def read_file(self, path: str):
        """Read file contents"""
        payload = {"path": path}
        response = self.session.post(f"{self.base_url}/files/read", json=payload)
        self._print_response(f"READ FILE: {path}", response)
        return response.json()
    
    def write_file(self, path: str, content: str, mode: str = "w"):
        """Write to file"""
        payload = {
            "path": path,
            "content": content,
            "mode": mode
        }
        response = self.session.post(f"{self.base_url}/files/write", json=payload)
        self._print_response(f"WRITE FILE: {path}", response)
        return response.json()
    
    def delete_file(self, path: str):
        """Delete file"""
        payload = {"path": path}
        response = self.session.post(f"{self.base_url}/files/delete", json=payload)
        self._print_response(f"DELETE FILE: {path}", response)
        return response.json()
    
    def create_directory(self, path: str):
        """Create directory"""
        payload = {"path": path}
        response = self.session.post(f"{self.base_url}/files/mkdir", json=payload)
        self._print_response(f"CREATE DIR: {path}", response)
        return response.json()
    
    # Process Endpoints
    def list_processes(self):
        """List all processes"""
        response = self.session.get(f"{self.base_url}/process/list")
        self._print_response("PROCESS LIST", response)
        return response.json()
    
    def get_process_info(self, pid: int):
        """Get process information"""
        response = self.session.get(f"{self.base_url}/process/info/{pid}")
        self._print_response(f"PROCESS INFO: PID {pid}", response)
        return response.json()
    
    def start_process(self, name: str, command: str = None, args: list = None):
        """Start a process"""
        payload = {
            "name": name,
            "command": command,
            "args": args or []
        }
        response = self.session.post(f"{self.base_url}/process/start", json=payload)
        self._print_response(f"START PROCESS: {name}", response)
        return response.json()
    
    def stop_process(self, pid: int):
        """Stop a process"""
        payload = {"pid": pid}
        response = self.session.post(f"{self.base_url}/process/stop", json=payload)
        self._print_response(f"STOP PROCESS: PID {pid}", response)
        return response.json()
    
    def get_process_stats(self):
        """Get process statistics"""
        response = self.session.get(f"{self.base_url}/process/stats")
        self._print_response("PROCESS STATS", response)
        return response.json()
    
    # Health Check
    def health_check(self):
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        self._print_response("HEALTH CHECK", response)
        return response.json()


def main():
    """
    Main demonstration function
    Shows various API interactions
    """
    print("\n" + "="*60)
    print("BACKEND API CLIENT - EXAMPLE USAGE")
    print("="*60)
    
    # Create client
    client = BackendAPIClient()
    
    # Wait for server to be ready
    print("\nWaiting for backend to be ready...")
    for i in range(10):
        try:
            client.health_check()
            print("✓ Backend is ready!")
            break
        except requests.exceptions.ConnectionError:
            print(f"Waiting... ({i+1}/10)")
            time.sleep(1)
    else:
        print("✗ Could not connect to backend. Make sure it's running:")
        print("  python backend/main.py")
        return
    
    # Demonstrate System APIs
    print("\n" + "="*60)
    print("SYSTEM API EXAMPLES")
    print("="*60)
    
    client.get_system_info()
    client.get_system_status()
    client.get_uptime()
    client.get_layers()
    
    # Demonstrate Shell APIs
    print("\n" + "="*60)
    print("SHELL API EXAMPLES")
    print("="*60)
    
    client.list_shell_commands()
    client.execute_command("help")
    client.execute_command("syscheck")
    
    # Batch execution
    client.execute_batch(["help", "uptime", "whoami"])
    
    # Demonstrate File APIs
    print("\n" + "="*60)
    print("FILE API EXAMPLES")
    print("="*60)
    
    client.list_files("/")
    
    # Try to write and read a file
    try:
        client.write_file("/test.txt", "Hello from Backend API!")
        client.read_file("/test.txt")
        client.delete_file("/test.txt")
    except Exception as e:
        print(f"File operations may not be fully supported: {e}")
    
    # Demonstrate Process APIs
    print("\n" + "="*60)
    print("PROCESS API EXAMPLES")
    print("="*60)
    
    client.list_processes()
    client.get_process_stats()
    
    print("\n" + "="*60)
    print("EXAMPLE USAGE COMPLETE")
    print("="*60)
    print("\nFor interactive API documentation, visit:")
    print("  http://localhost:8000/docs")
    print("\nFor alternative documentation, visit:")
    print("  http://localhost:8000/redoc")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
