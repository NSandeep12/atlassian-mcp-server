@echo off
REM Cross-platform Jira MCP Server Management Script for Windows
REM Usage: server.bat [start|stop|restart|status]

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

REM Check if Python script exists
if not exist "jira_server.py" (
    echo [ERROR] jira_server.py not found in current directory
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)

REM Handle commands
if "%1"=="start" (
    echo [INFO] Starting Jira MCP Server...
    python server_manager.py start
    goto :end
)

if "%1"=="stop" (
    echo [INFO] Stopping Jira MCP Server...
    python server_manager.py stop
    goto :end
)

if "%1"=="restart" (
    echo [INFO] Restarting Jira MCP Server...
    python server_manager.py restart
    goto :end
)

if "%1"=="status" (
    echo [INFO] Checking Jira MCP Server status...
    python server_manager.py status
    goto :end
)

REM Default case - show usage
echo Usage: %0 [start^|stop^|restart^|status]
echo.
echo Commands:
echo   start   - Start the Jira MCP server
echo   stop    - Stop the Jira MCP server
echo   restart - Restart the Jira MCP server
echo   status  - Show server status
echo.
echo Examples:
echo   %0 start    # Start the server
echo   %0 status   # Check if server is running
echo   %0 stop     # Stop the server
exit /b 1

:end
endlocal
