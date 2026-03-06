# Open-Coder-Agent

Open Source coder agent that uses issues on Git as prompts joined with codebase in order to generate pull requests solving them

## Requirements

- [Docker](https://docs.docker.com/engine/install/)
- [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Planka

Planka is an Open Source easy-to-use Kanban management system that can configure webhooks to link to another applications

Basic setup

1. Create a secret with `openssl rand -hex 64` and include it in the `.env` as PLANKA_SECRET
2. Launch an init container to setup admin account `docker compose run --rm planka npm run db:create-admin-user`

## API / Agent

FastAPI is fully integrated with [uv](https://docs.astral.sh/uv). For development purposes, install uv and all needed dependencies

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

`pyproject.toml` is already provided with Python version, needed dependencies and configuration for code static analysis

`uv sync --all-groups --no-cache` to install all dependencies

Install `pre-commit` to run code checks on commit phase

```bash
uv run pre-commit install
uv run pre-commit run --all-files # test pre-commit on code manually
```

## Run API

```bash
uv run fastapi run api/src/main.py --port 8080
```
