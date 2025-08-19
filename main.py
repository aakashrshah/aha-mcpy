#!/usr/bin/env python3
"""
Main entry point for the Aha! MCP Server
"""

import argparse
import os
import logging

try:
    from .server import mcp
except ImportError:
    from server import mcp

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description="Aha! MCP Server - FastMCP HTTP Streaming")
    parser.add_argument("--transport", type=str, default="streamable-http")
    args = parser.parse_args()
    
    if args.transport == "stdio":
        logger.info("Aha! MCP Server starting with stdio transport")
        mcp.run()
    else:   
        logger.info("Aha! MCP Server starting with streamable-http transport")
        mcp.run(
            transport=os.getenv("MCP_TRANSPORT_TYPE", "streamable-http"),
            host=os.getenv("MCP_SERVER_AHA_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_SERVER_AHA_PORT", "9004")),
        )
    logger.info("Aha! MCP Server ready")
