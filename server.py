#!/usr/bin/env python3
"""
Aha! MCP Server - Python FastMCP HTTP Streaming Implementation
"""

import os
import logging
import argparse
from typing import Any, Dict
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from fastmcp import FastMCP

try:
    from .handlers import Handlers
except ImportError:
    from handlers import Handlers


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_aha_credentials():
    """Get Aha! API credentials from environment variables"""
    aha_api_token = os.getenv("AHA_API_TOKEN")
    aha_domain = os.getenv("AHA_DOMAIN")
    
    if not aha_api_token:
        raise ValueError("AHA_API_TOKEN environment variable is required")
    
    if not aha_domain:
        raise ValueError("AHA_DOMAIN environment variable is required")
    
    return aha_api_token, aha_domain


def create_graphql_client(aha_domain: str, aha_api_token: str) -> Client:
    """Create GraphQL client for Aha! API"""
    transport = AIOHTTPTransport(
        url=f"https://{aha_domain}.aha.io/api/v2/graphql",
        headers={
            "Authorization": f"Bearer {aha_api_token}",
            "Content-Type": "application/json"
        }
    )
    
    return Client(transport=transport, fetch_schema_from_transport=False)


# Initialize the server
mcp = FastMCP("aha-mcp")

# Initialize GraphQL client and handlers at module level
try:
    aha_api_token, aha_domain = get_aha_credentials()
    logger.info(f"Initializing Aha! MCP server for domain: {aha_domain}")
    
    graphql_client = create_graphql_client(aha_domain, aha_api_token)
    handlers = Handlers(graphql_client)
    
    logger.info("Aha! MCP server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Aha! MCP server: {e}")
    handlers = None


@mcp.tool()
async def get_record(reference: str) -> str:
    """
    Get an Aha! feature or requirement by reference number
    
    Args:
        reference: Reference number (e.g., DEVELOP-123 or ADT-123-1)
    
    Returns:
        JSON string containing the record details
    """
    if not handlers:
        return "❌ Error: Handlers not initialized"
    
    return await handlers.handle_get_record({"reference": reference})


@mcp.tool()
async def get_page(reference: str, include_parent: bool = False) -> str:
    """
    Get an Aha! page by reference number with optional relationships
    
    Args:
        reference: Reference number (e.g., ABC-N-213)
        include_parent: Include parent page in the response
    
    Returns:
        JSON string containing the page details
    """
    if not handlers:
        return "❌ Error: Handlers not initialized"
    
    return await handlers.handle_get_page({
        "reference": reference,
        "includeParent": include_parent
    })


@mcp.tool()
async def search_documents(query: str, searchable_type: str = "Page") -> str:
    """
    Search for Aha! documents
    
    Args:
        query: Search query string
        searchable_type: Type of document to search for (e.g., Page)
    
    Returns:
        JSON string containing the search results
    """
    if not handlers:
        return "❌ Error: Handlers not initialized"
    
    return await handlers.handle_search_documents({
        "query": query,
        "searchableType": searchable_type
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aha! MCP Server - FastMCP HTTP Streaming")
    parser.add_argument("--transport", type=str, default="streamable-http")
    args = parser.parse_args()
    
    if args.transport == "stdio":
        logger.info("Aha! MCP Server starting with stdio transport")
        mcp.run()
    else:   
        logger.info("Aha! MCP Server starting with streamable-http transport")
        mcp.run(
            transport="streamable-http",
            host=os.getenv("MCP_SERVER_AHA_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_SERVER_AHA_PORT", "9004")),
        )
    logger.info("Aha! MCP Server ready")
