FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ src/

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "lcars-mcp-server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
