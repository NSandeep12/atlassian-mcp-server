#!/usr/bin/env python3
"""
Main entry point for the Atlassian MCP Server
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jira_bitbucket_server import main as run_server

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('atlassian-mcp-server.log')
        ]
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Atlassian MCP Server - Jira & Bitbucket Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start server with default settings
  python main.py --debug           # Start with debug logging
  python main.py --config custom.env  # Use custom config file
        """
    )
    
    parser.add_argument(
        '--config',
        default='.env',
        help='Configuration file path (default: .env)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Atlassian MCP Server v1.0.0")
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        logger.info("Please copy config/.env.example to .env and configure your settings")
        sys.exit(1)
    
    try:
        # Start the server
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
