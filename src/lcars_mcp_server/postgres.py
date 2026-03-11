"""Postgres connection and source metadata queries."""

import json

from psycopg_pool import ConnectionPool

from lcars_mcp_server.settings import POSTGRES_URL, METADATA_TABLE

pool = ConnectionPool(POSTGRES_URL, min_size=1, max_size=5)


def get_sources(source_name: str | None = None) -> list[dict]:
    """Return source metadata rows, optionally filtered by name."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if source_name:
                cur.execute(
                    f"SELECT source_name, source_type, url, tags, file_count "
                    f"FROM {METADATA_TABLE} WHERE source_name = %s "
                    f"ORDER BY source_name",
                    (source_name,),
                )
            else:
                cur.execute(
                    f"SELECT source_name, source_type, url, tags, file_count "
                    f"FROM {METADATA_TABLE} ORDER BY source_name"
                )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [_row_to_dict(columns, row) for row in rows]


def get_tags(source_name: str | None = None) -> list[str]:
    """Return sorted unique tags, optionally filtered by source."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if source_name:
                cur.execute(
                    f"SELECT DISTINCT jsonb_array_elements_text(tags) AS tag "
                    f"FROM {METADATA_TABLE} WHERE source_name = %s "
                    f"ORDER BY tag",
                    (source_name,),
                )
            else:
                cur.execute(
                    f"SELECT DISTINCT jsonb_array_elements_text(tags) AS tag "
                    f"FROM {METADATA_TABLE} ORDER BY tag"
                )
            return [row[0] for row in cur.fetchall()]


def get_source_names_by_tags(tags: list[str]) -> list[str]:
    """Return source_names where ALL given tags are present."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT source_name FROM {METADATA_TABLE} "
                f"WHERE tags @> %s ORDER BY source_name",
                (json.dumps(tags),),
            )
            return [row[0] for row in cur.fetchall()]


def get_metadata_map(source_names: list[str]) -> dict[str, dict]:
    """Batch-fetch metadata for a list of source_names. Returns {name: {...}}."""
    if not source_names:
        return {}
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT source_name, source_type, url, tags, file_count "
                f"FROM {METADATA_TABLE} WHERE source_name = ANY(%s)",
                (source_names,),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return {row[0]: _row_to_dict(columns, row) for row in rows}


def _row_to_dict(columns: list[str], row: tuple) -> dict:
    d = dict(zip(columns, row))
    # Ensure tags is always a list
    if isinstance(d.get("tags"), str):
        try:
            d["tags"] = json.loads(d["tags"])
        except (json.JSONDecodeError, TypeError):
            d["tags"] = []
    elif d.get("tags") is None:
        d["tags"] = []
    return d
