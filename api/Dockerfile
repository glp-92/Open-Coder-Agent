FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --no-dev --frozen --no-cache
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "8080", "--host", "0.0.0.0"]