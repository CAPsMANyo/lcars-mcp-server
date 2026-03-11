#!/usr/bin/env python3
"""LCARS MCP Server - Search code and doc embeddings in Qdrant."""

from fastmcp import FastMCP

mcp = FastMCP("lcars-mcp-server")

# Import functions to register @mcp.tool() decorators
import lcars_mcp_server.functions  # noqa: E402, F401
