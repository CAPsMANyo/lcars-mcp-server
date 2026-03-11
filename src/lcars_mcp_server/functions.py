"""MCP tool definitions for LCARS search."""

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchText,
    MatchValue,
)

from lcars_mcp_server.embeddings import embed_query
from lcars_mcp_server.qdrant import format_result, parse_tags, qdrant
from lcars_mcp_server.server import mcp
from lcars_mcp_server.settings import QDRANT_COLLECTION


@mcp.tool()
def search(
    query: str,
    source_name: str | None = None,
    tags: list[str] | None = None,
    language: str | None = None,
    content_type: str | None = None,
    filename: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search code and documentation embeddings.

    Args:
        query: Natural language search query.
        source_name: Filter by repository name (e.g. "cocoindex", "frigate").
        tags: Filter by tags (e.g. ["rag", "ai"]). All tags must match.
        language: Filter by programming language (e.g. "python", "rust").
        content_type: Filter by "code" or "docs".
        filename: Filter by filename substring (e.g. "src/main" matches "src/main.py").
        limit: Max results to return (default 10).
    """
    conditions = []

    if source_name:
        conditions.append(FieldCondition(key="source_name", match=MatchValue(value=source_name)))
    if language:
        conditions.append(FieldCondition(key="language", match=MatchValue(value=language)))
    if content_type:
        conditions.append(FieldCondition(key="content_type", match=MatchValue(value=content_type)))
    if filename:
        conditions.append(FieldCondition(key="filename", match=MatchText(text=filename)))
    if tags:
        for tag in tags:
            conditions.append(FieldCondition(key="tags", match=MatchValue(value=tag)))

    query_filter = Filter(must=conditions) if conditions else None
    vector = embed_query(query)

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )

    return [format_result(point) for point in results.points]


@mcp.tool()
def list_sources() -> list[dict]:
    """List all indexed source repositories."""
    sources = {}
    offset = None

    while True:
        result = qdrant.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=100,
            offset=offset,
            with_payload=["source_name", "url", "source_type"],
            with_vectors=False,
        )
        points, offset = result

        for point in points:
            name = point.payload.get("source_name")
            if name and name not in sources:
                sources[name] = {
                    "source_name": name,
                    "url": point.payload.get("url"),
                    "source_type": point.payload.get("source_type"),
                }

        if offset is None:
            break

    return sorted(sources.values(), key=lambda s: s["source_name"])


@mcp.tool()
def list_tags(source_name: str | None = None) -> list[str]:
    """List all unique tags across indexed sources.

    Args:
        source_name: Optionally filter to tags from a specific source.
    """
    all_tags = set()
    offset = None
    query_filter = None

    if source_name:
        query_filter = Filter(
            must=[FieldCondition(key="source_name", match=MatchValue(value=source_name))]
        )

    while True:
        result = qdrant.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=query_filter,
            limit=100,
            offset=offset,
            with_payload=["tags"],
            with_vectors=False,
        )
        points, offset = result

        for point in points:
            tags = parse_tags(point.payload.get("tags", "[]"))
            all_tags.update(tags)

        if offset is None:
            break

    return sorted(all_tags)
