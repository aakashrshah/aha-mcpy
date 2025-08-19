# Aha! MCP Server - Python FastMCP Implementation

A Python-based MCP server for interacting with Aha! API using FastMCP with HTTP streaming capabilities.

## Features

- **HTTP Streaming**: Built with FastMCP for efficient HTTP streaming
- **GraphQL Integration**: Uses GraphQL to query Aha! API
- **Three Main Tools**:
  - `get_record`: Get features or requirements by reference number
  - `get_page`: Get pages with optional parent relationships
  - `search_documents`: Search for Aha! documents

## Environment Variables

- `AHA_API_TOKEN`: Your Aha! API token (required)
- `AHA_DOMAIN`: Your Aha! domain name (required)
- `PORT`: Server port (default: 9004)

## Installation

```bash
pip install -r requirements.txt
```

## Running

### Local Development
```bash
# Set environment variables
export AHA_API_TOKEN="your_token_here"
export AHA_DOMAIN="your_domain_here"

# Run with HTTP streaming (default)
python main.py

# Or run with stdio transport
python main.py --transport stdio
```

### Docker
```bash
# Build the image
docker build -t aha-mcp .

# Run the container
docker run -e AHA_API_TOKEN="your_token_here" -e AHA_DOMAIN="your_domain_here" -p 9004:9004 aha-mcp
```

## Tools

### get_record
Get an Aha! feature or requirement by reference number.
- **Input**: reference (string) - e.g., "DEVELOP-123" or "ADT-123-1"
- **Output**: JSON with name and description

### get_page  
Get an Aha! page by reference number with optional relationships.
- **Input**: 
  - reference (string) - e.g., "ABC-N-213"
  - include_parent (boolean, optional) - Include parent page
- **Output**: JSON with page details, children, and optional parent

### search_documents
Search for Aha! documents.
- **Input**:
  - query (string) - Search query
  - searchable_type (string, optional) - Document type (default: "Page")
- **Output**: JSON with search results and pagination info

## Architecture

- `server.py`: Main FastMCP server with tool definitions
- `handlers.py`: Business logic for handling each tool
- `queries.py`: GraphQL queries for Aha! API  
- `types.py`: Python dataclasses for type safety
- `main.py`: Entry point for running the server

Inspired from https://github.com/aha-develop/aha-mcp
