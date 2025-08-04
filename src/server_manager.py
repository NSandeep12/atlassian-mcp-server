#!/usr/bin/env python3
"""
Cross-platform Jira MCP Server Manager
Handles starting, stopping, and managing the Jira MCP server across different operating systems.
"""

import os
import sys
import platform
import subprocess
import signal
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class ServerManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.pid_file = self.script_dir / "server.pid"
        self.log_file = self.script_dir / "server_manager.log"
        self.server_script = self.script_dir / "jira_server.py"
        self.venv_path = self.script_dir / "venv"
        
        # Setup logging
        self.setup_logging()
        
        # Detect OS
        self.os_type = self.detect_os()
        self.logger.info(f"Detected OS: {self.os_type}")
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def detect_os(self) -> str:
        """Detect the current operating system"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            self.logger.warning(f"Unknown OS: {system}, defaulting to linux")
            return "linux"
    
    def get_python_executable(self) -> str:
        """Get the appropriate Python executable path"""
        if self.os_type == "windows":
            python_exe = self.venv_path / "Scripts" / "python.exe"
        else:
            python_exe = self.venv_path / "bin" / "python"
            
        if python_exe.exists():
            return str(python_exe)
        else:
            self.logger.warning("Virtual environment not found, using system Python")
            return sys.executable
    
    def is_server_running(self) -> bool:
        """Check if the server is currently running"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            # Check if process is still running
            if self.os_type == "windows":
                # Windows process check
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True
                )
                return str(pid) in result.stdout
            else:
                # Unix-like process check
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    return True
                except OSError:
                    return False
                    
        except (ValueError, FileNotFoundError):
            return False
    
    def start_server(self) -> bool:
        """Start the Jira MCP server"""
        if self.is_server_running():
            self.logger.info("Server is already running")
            return True
            
        self.logger.info("Starting Jira MCP server...")
        
        try:
            python_exe = self.get_python_executable()
            
            # Start the server process
            if self.os_type == "windows":
                # Windows: Use CREATE_NEW_PROCESS_GROUP to allow clean shutdown
                process = subprocess.Popen(
                    [python_exe, str(self.server_script)],
                    cwd=str(self.script_dir),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Unix-like: Use nohup equivalent
                process = subprocess.Popen(
                    [python_exe, str(self.server_script)],
                    cwd=str(self.script_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
                
            # Give the server a moment to start
            time.sleep(2)
            
            if self.is_server_running():
                self.logger.info(f"Server started successfully with PID {process.pid}")
                return True
            else:
                self.logger.error("Server failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the Jira MCP server"""
        if not self.is_server_running():
            self.logger.info("Server is not running")
            return True
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            self.logger.info(f"Stopping server with PID {pid}...")
            
            if self.os_type == "windows":
                # Windows: Use taskkill
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            else:
                # Unix-like: Use kill
                os.kill(pid, signal.SIGTERM)
                
                # Wait for graceful shutdown
                for _ in range(10):
                    if not self.is_server_running():
                        break
                    time.sleep(1)
                
                # Force kill if still running
                if self.is_server_running():
                    self.logger.warning("Forcing server shutdown...")
                    os.kill(pid, signal.SIGKILL)
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
                
            self.logger.info("Server stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop server: {e}")
            return False
    
    def restart_server(self) -> bool:
        """Restart the Jira MCP server"""
        self.logger.info("Restarting server...")
        if self.stop_server():
            time.sleep(2)
            return self.start_server()
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status information"""
        is_running = self.is_server_running()
        status = {
            "running": is_running,
            "os": self.os_type,
            "pid": None,
            "uptime": None
        }
        
        if is_running and self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    status["pid"] = int(f.read().strip())
                    
                # Get file modification time as start time approximation
                start_time = self.pid_file.stat().st_mtime
                uptime_seconds = time.time() - start_time
                status["uptime"] = f"{uptime_seconds:.0f} seconds"
                
            except Exception:
                pass
                
        return status
    
    def print_status(self):
        """Print formatted status information"""
        status = self.get_status()
        
        print(f"🖥️  OS: {status['os'].title()}")
        print(f"🔄 Status: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
        
        if status['running']:
            print(f"🆔 PID: {status['pid']}")
            if status['uptime']:
                print(f"⏱️  Uptime: {status['uptime']}")
        
        print(f"📁 Working Directory: {self.script_dir}")
        print(f"📝 Log File: {self.log_file}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python server_manager.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = ServerManager()
    
    if command == "start":
        success = manager.start_server()
        sys.exit(0 if success else 1)
        
    elif command == "stop":
        success = manager.stop_server()
        sys.exit(0 if success else 1)
        
    elif command == "restart":
        success = manager.restart_server()
        sys.exit(0 if success else 1)
        
    elif command == "status":
        manager.print_status()
        sys.exit(0)
        
    else:
        print(f"Unknown command: {command}")
        print("Usage: python server_manager.py [start|stop|restart|status]")
        sys.exit(1)

if __name__ == "__main__":
    main()
