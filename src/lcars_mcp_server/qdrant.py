"""Qdrant client and helper functions."""

import json

from qdrant_client import QdrantClient

from lcars_mcp_server.settings import QDRANT_API_KEY, QDRANT_URL

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, prefer_grpc=True)


def parse_tags(tags_field) -> list[str]:
    """Parse tags from JSON string or return as-is if already a list."""
    if isinstance(tags_field, list):
        return tags_field
    if isinstance(tags_field, str):
        try:
            return json.loads(tags_field)
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def format_result(point) -> dict:
    """Format a Qdrant point into a clean result dict."""
    payload = point.metadata if hasattr(point, "metadata") else point.payload
    return {
        "score": round(point.score, 4) if hasattr(point, "score") else None,
        "source_name": payload.get("source_name"),
        "filename": payload.get("filename"),
        "url": payload.get("url"),
        "language": payload.get("language"),
        "content_type": payload.get("content_type"),
        "tags": parse_tags(payload.get("tags", "[]")),
        "chunk_text": payload.get("chunk_text"),
    }
