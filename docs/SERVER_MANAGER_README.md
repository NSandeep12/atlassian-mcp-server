# Jira MCP Server Manager

Cross-platform automation scripts to start, stop, and manage the Jira MCP server across different operating systems (Windows, macOS, Linux).

## Features

- ✅ **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- 🔍 **OS detection** - Automatically detects the operating system
- 📊 **Process management** - Start, stop, restart, and status checking
- 📝 **Comprehensive logging** - Detailed logs for troubleshooting
- 🔄 **Virtual environment handling** - Automatic venv activation
- 🆔 **PID management** - Tracks running processes with PID files
- 🛡️ **Error handling** - Graceful error handling and recovery
- 🎯 **Unified interface** - Same commands work across all platforms

## Quick Start

### Linux/macOS
```bash
# Start the server
./server.sh start

# Check status
./server.sh status

# Stop the server
./server.sh stop

# Restart the server
./server.sh restart
```

### Windows
```cmd
# Start the server
server.bat start

# Check status
server.bat status

# Stop the server
server.bat stop

# Restart the server
server.bat restart
```

### Python (All platforms)
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate.bat  # Windows

# Then use the Python script directly
python server_manager.py start
python server_manager.py status
python server_manager.py stop
python server_manager.py restart
```

## Installation

1. **Ensure virtual environment is set up:**
   ```bash
   # If not already done
   ./setup.sh  # Linux/macOS
   # OR
   setup.bat   # Windows
   ```

2. **Make scripts executable (Linux/macOS only):**
   ```bash
   chmod +x server.sh
   ```

3. **Test the installation:**
   ```bash
   ./server.sh status  # Linux/macOS
   server.bat status   # Windows
   ```

## Commands

| Command | Description |
|---------|-------------|
| `start` | Start the Jira MCP server |
| `stop` | Stop the Jira MCP server |
| `restart` | Restart the Jira MCP server |
| `status` | Show current server status |

## File Structure

```
jira-mcp-server/
├── server_manager.py      # Main Python server manager
├── server.sh             # Linux/macOS shell script
├── server.bat            # Windows batch script
├── server.pid            # Process ID file (created when running)
├── server_manager.log    # Server manager log file
├── jira_server.py        # Main Jira MCP server script
└── venv/                 # Virtual environment
```

## Status Information

The status command provides detailed information:

- 🖥️ **Operating System** - Detected OS type
- 🔄 **Status** - Running (🟢) or Stopped (🔴)
- 🆔 **Process ID** - PID of the running server
- ⏱️ **Uptime** - How long the server has been running
- 📁 **Working Directory** - Current script location
- 📝 **Log File** - Location of log files

## Logging

All operations are logged to `server_manager.log` with timestamps:

```
2024-07-25 19:00:00 - INFO - Detected OS: linux
2024-07-25 19:00:01 - INFO - Starting Jira MCP server...
2024-07-25 19:00:03 - INFO - Server started successfully with PID 12345
```

## Error Handling

The scripts include comprehensive error handling:

- **Virtual environment checks** - Ensures venv exists before starting
- **Process validation** - Verifies server script exists
- **Graceful shutdown** - Attempts SIGTERM before SIGKILL (Unix)
- **PID file management** - Cleans up stale PID files
- **Permission checks** - Validates script permissions

## Platform-Specific Features

### Linux/macOS
- Uses `os.setsid()` for proper process group management
- Implements graceful shutdown with SIGTERM/SIGKILL
- Color-coded shell output for better visibility
- Uses `/bin/bash` for better compatibility

### Windows
- Uses `CREATE_NEW_PROCESS_GROUP` for process management
- Implements `taskkill` for process termination
- Batch script with proper error level handling
- Windows-specific path handling

## Troubleshooting

### Common Issues

1. **"Virtual environment not found"**
   ```bash
   # Run setup first
   ./setup.sh  # Linux/macOS
   setup.bat   # Windows
   ```

2. **"Permission denied" (Linux/macOS)**
   ```bash
   chmod +x server.sh
   ```

3. **"Server failed to start"**
   - Check `server_manager.log` for detailed error messages
   - Ensure `jira_server.py` exists
   - Verify virtual environment is properly set up

4. **"Process not found" errors**
   - Remove stale `server.pid` file
   - Restart the server

### Debug Mode

For detailed debugging, check the log file:
```bash
tail -f server_manager.log
```

## Integration Examples

### With systemd (Linux)
```ini
[Unit]
Description=Jira MCP Server
After=network.target

[Service]
Type=forking
User=your-user
WorkingDirectory=/path/to/jira-mcp-server
ExecStart=/path/to/jira-mcp-server/server.sh start
ExecStop=/path/to/jira-mcp-server/server.sh stop
Restart=always

[Install]
WantedBy=multi-user.target
```

### With cron (Linux/macOS)
```bash
# Start server on boot
@reboot /path/to/jira-mcp-server/server.sh start

# Health check every 5 minutes
*/5 * * * * /path/to/jira-mcp-server/server.sh status || /path/to/jira-mcp-server/server.sh start
```

### With Task Scheduler (Windows)
Create a scheduled task that runs:
```
Program: C:\path\to\jira-mcp-server\server.bat
Arguments: start
```

## Security Considerations

- Scripts run with current user permissions
- PID files are created with restricted permissions
- Log files may contain sensitive information
- Virtual environment isolation provides security boundaries

## Contributing

When modifying the server manager:

1. Test on all supported platforms
2. Update documentation
3. Add appropriate error handling
4. Follow existing logging patterns
5. Maintain backward compatibility
