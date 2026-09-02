# Peter - Windows Native AI Butler

Peter is a lightweight, local-first autonomous agent ecosystem designed for Windows desktop environments.

## Features
- **Local LLM Backend**: Integrates natively with [Ollama](https://ollama.ai/) for secure, offline processing.
- **Dynamic MCP Plugins**: Scalable Model Context Protocol architecture for extending OS tools.
- **System Tray Integration**: Unobtrusive `pystray`-based background presence.
- **Safety Guardrails**: Built-in protections against destructive OS commands and restricted directories.

## Setup & Environment
1. Install [Ollama](https://ollama.ai/) and run `ollama run phi3:mini`.
2. Run `start.bat`. This script will:
   - Create a Python Virtual Environment (`venv`)
   - Install dependencies from `requirements.txt`
   - Copy `.env.example` to `.env`
   - Launch `main.py`

## Configuration
Edit the `.env` file to customize Peter's behavior:
- `OLLAMA_HOST` & `OLLAMA_MODEL`: Point Peter to your preferred local model.
- `ALLOW_DESTRUCTIVE_COMMANDS`: Enable/Disable guardrails.

## Extended UI
The `ui/web/` directory has been scaffolded to support a future React/Vue or HTML dashboard.
