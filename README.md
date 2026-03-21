# LCARS MCP Server

MCP server for searching code and documentation embeddings stored in Qdrant.

## Prerequisites

- Python 3.12+
- Running Qdrant instance with indexed embeddings (from lcars-rag)
- Running PostgreSQL instance with source metadata (from lcars-rag)
- An OpenAI-compatible embedding API (for query embedding)

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and configure
3. Install: `uv sync`

## Configuration

All settings via environment variables (see `.env.example`):

- `QDRANT_URL`, `QDRANT_COLLECTION` -- vector database
- `POSTGRES_URL`, `METADATA_TABLE` -- source metadata
- `EMBEDDING_API_ADDRESS`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION` -- query embedding
- `RERANK_ENABLED`, `RERANK_API_ADDRESS`, `RERANK_MODEL`, `RERANK_TOP_N` -- optional reranking

## Usage

Run with stdio (for MCP clients like Claude):

```
lcars-mcp-server
```

Run with HTTP transport:

```
lcars-mcp-server --transport streamable-http --port 8000
```

## MCP Tools

- `search` -- semantic search across indexed code and docs, with filters for source, tags, language, content type, and filename
- `list_sources` -- list all indexed repositories with metadata
- `list_tags` -- list available tags, optionally filtered by source
- `get_source` -- get details for a specific source by name
- `find_files` -- find files by name pattern without semantic search
- `search_sources` -- filter sources by tags or type

## MCP Client Configuration

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "lcars": {
      "command": "lcars-mcp-server",
      "args": []
    }
  }
}
```

Claude Code (`.mcp.json`):

```json
{
  "mcpServers": {
    "lcars": {
      "command": "lcars-mcp-server",
      "args": []
    }
  }
}
```
