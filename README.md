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
