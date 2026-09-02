# Research: Architecture

## Core Patterns
An asynchronous, event-driven architecture is mandatory to prevent the "jamming" effect caused by continuous voice input while the LLM is still processing.

### 1. The Async Event Loop
The heart of Peter will be an `asyncio` event loop that manages three primary workers:
*   **Listener (Producer)**: Constantly records audio, cuts it upon VAD silence, runs `faster-whisper`, and pushes transcribed text to the `IntentQueue`.
*   **Processor (Consumer)**: Pops from `IntentQueue`, routes to Local LLM (or MCP tools), and yields text tokens.
*   **Speaker (Consumer)**: Takes text output, runs `piper-tts`, and outputs audio.

### 2. Context Queuing Mechanism
*   **Voice Note Buffer**: A strict FIFO queue. If Peter is currently thinking/speaking, new transcribed inputs are pushed to this queue and acknowledged with a short audio ping (e.g., "Queued").
*   **Context Limit**: The local model is strictly capped (e.g., 4096 tokens). The `Processor` maintains a rolling memory window.

### 3. Dynamic MCP Plugin System
*   **Registry**: A central `MCPManager` dynamically crawls a `/plugins/` directory on startup.
*   **Hot-Swapping**: The UI (via `pystray`) has access to toggle these servers on/off in real-time, instantly modifying the LLM's system prompt to reflect available tools.

### 4. TDD / Module Isolation
*   `core/`: LLM integration, Guardrails.
*   `audio/`: STT, TTS, VAD, Queues.
*   `ui/`: System tray, configuration popups.
*   `mcp/`: Plugin management and default OS tools.
*   `tests/`: `pytest` suite ensuring each pipeline acts independently.
