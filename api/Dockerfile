FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./api /app
COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock
WORKDIR /app
RUN uv sync --group api --no-dev --no-cache
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "8080", "--host", "0.0.0.0"]