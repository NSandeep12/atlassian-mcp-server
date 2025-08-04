#!/bin/bash
# Cross-platform Jira MCP Server Management Script for Linux/macOS
# Usage: ./server.sh [start|stop|restart|status]

set -e  # Exit on any error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    log "Activating virtual environment..."
    source venv/bin/activate
    if [ $? -eq 0 ]; then
        success "Virtual environment activated"
    else
        error "Failed to activate virtual environment"
        exit 1
    fi
}

# Check if Python script exists
check_server_script() {
    if [ ! -f "jira_server.py" ]; then
        error "jira_server.py not found in current directory"
        exit 1
    fi
}

# Main function to handle commands
case "${1:-}" in
    start)
        log "Starting Jira MCP Server..."
        check_venv
        check_server_script
        activate_venv
        python server_manager.py start
        ;;
    stop)
        log "Stopping Jira MCP Server..."
        check_venv
        activate_venv
        python server_manager.py stop
        ;;
    restart)
        log "Restarting Jira MCP Server..."
        check_venv
        activate_venv
        python server_manager.py restart
        ;;
    status)
        log "Checking Jira MCP Server status..."
        check_venv
        activate_venv
        python server_manager.py status
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status]"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Jira MCP server"
        echo "  stop    - Stop the Jira MCP server"
        echo "  restart - Restart the Jira MCP server"
        echo "  status  - Show server status"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the server"
        echo "  $0 status   # Check if server is running"
        echo "  $0 stop     # Stop the server"
        exit 1
        ;;
esac
