# LCARS MCP Server

MCP server for searching code and documentation embeddings stored in Qdrant. This package is intended to be used as a dependency in the [lcars-rag](https://github.com/CAPsMANyo/lcars-rag) project and should not be run standalone.

## Prerequisites

- Python 3.12+
- Running Qdrant instance with indexed embeddings (from lcars-rag)
- Running PostgreSQL instance with source metadata (from lcars-rag)
- An OpenAI-compatible embedding API (for query embedding)
