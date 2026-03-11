"""MCP tool definitions for LCARS search."""

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    MatchText,
    MatchValue,
)

from lcars_mcp_server.embeddings import embed_query
from lcars_mcp_server.postgres import get_metadata_map, get_source_names_by_tags, get_sources, get_tags
from lcars_mcp_server.qdrant import format_result, qdrant
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

    # Tags live in postgres now — resolve to source_names, then filter qdrant
    if tags:
        matching_sources = get_source_names_by_tags(tags)
        if not matching_sources:
            return []
        # If also filtering by source_name, intersect
        if source_name:
            if source_name not in matching_sources:
                return []
        else:
            conditions.append(
                FieldCondition(key="source_name", match=MatchAny(any=matching_sources))
            )

    query_filter = Filter(must=conditions) if conditions else None
    vector = embed_query(query)

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        using="embedding",
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )

    # Enrich results with metadata from postgres (url, tags)
    source_names = list({
        (p.metadata if hasattr(p, "metadata") else p.payload).get("source_name")
        for p in results.points
    })
    meta_map = get_metadata_map(source_names)

    return [
        format_result(
            point,
            metadata=meta_map.get(
                (point.metadata if hasattr(point, "metadata") else point.payload).get("source_name"),
                {},
            ),
        )
        for point in results.points
    ]


@mcp.tool()
def list_sources() -> list[dict]:
    """List all indexed source repositories."""
    return get_sources()


@mcp.tool()
def list_tags(source_name: str | None = None) -> list[str]:
    """List all unique tags across indexed sources.

    Args:
        source_name: Optionally filter to tags from a specific source.
    """
    return get_tags(source_name)
