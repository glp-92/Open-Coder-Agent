# Open-Coder-Agent

# Resumen de utilidad

Open-Coder-Agent es un agente de código local/offline enfocado en ser ligero, minimalista y útil para desarrollo diario.

Su objetivo principal es:

- Recibir prompts de trabajo técnico sobre un repositorio.
- Inspeccionar y modificar código usando tools internas optimizadas.
- Ejecutar un flujo de agente con modelo local en Ollama.

El proyecto está pensado para ejecutarse en entorno local con foco en control, bajo consumo y rapidez de iteración.

# Servicios que implementa

Actualmente el stack se mantiene deliberadamente pequeño:

- `ollama-server`: servidor local de modelos LLM para ejecución offline.

Además, el repositorio incluye:

- `agent/`: núcleo del agente (grafo, modelo, tools y CLI).
- `leann/`: submódulo/librería de recuperación y utilidades de IA.

# Instalacion

## 1) Requisitos

- [Docker](https://docs.docker.com/engine/install/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (si se usará GPU)
- [uv](https://docs.astral.sh/uv/) para entorno Python en desarrollo

## 2) Variables de entorno

Crear `.env` en la raíz (puedes partir de `.env.example`) y completar al menos:

- `MODEL_NAME`
- `OLLAMA_URL`
- `REPOSITORY_ROOT_PATH`

## 3) Dependencias Python (desarrollo)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
uv sync --all-groups --no-cache
```

## 4) Configuración opcional de pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

# Instrucciones de uso

## Levantar servicios con Docker

```bash
docker compose up -d
```

## Ejecutar agente por CLI

El agente recibe el prompt como argumento:

```bash
./agent-run "tu prompt aqui"
```

### Uso desde cualquier repositorio objetivo

Si ya estás parado en el repositorio donde quieres que el agente trabaje:

```bash
REPOSITORY_ROOT_PATH="$PWD" /home/glp-desktop/Workspace/Open-Coder-Agent/agent-run "tu prompt aqui"
```

Eso ejecuta el agente instalado en Open-Coder-Agent, pero operando sobre el repo actual (`$PWD`).

Comando avanzado equivalente (solo si lo necesitas):

```bash
REPOSITORY_ROOT_PATH="$PWD" uv --directory /home/glp-desktop/Workspace/Open-Coder-Agent run python agent/src/main.py "tu prompt aqui"
```

Ejemplo:

```bash
./agent-run "revisa el modulo de tools y propone mejoras de rendimiento"
```

## Verificación rápida de calidad

```bash
uv run ruff check agent
```
