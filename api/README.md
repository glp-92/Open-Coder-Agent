# Service API

API for communicating services using Python FastAPI.

1. Receives webhooks from boards with user stories

## Setup

FastAPI currently integrates with [uv](https://docs.astral.sh/uv). For development purposes, install uv and all needed dependencies

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

`pyproject.toml` is already provided with Python version, needed dependencies and configuration for code static analysis

Install `pre-commit` to run code checks on commit phase

```bash
uv run pre-commit install
uv run pre-commit run --all-files # test pre-commit on code manually
```

## Run API

```bash
uv run fastapi run src/main.py --port 8080
```
