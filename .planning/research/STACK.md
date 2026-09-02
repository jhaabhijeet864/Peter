# Research: Stack (Polyglot Architecture)

## Summary
The optimal 2026 stack for Peter utilizes a **Hybrid Polyglot Architecture**, leveraging the strengths of both TypeScript and Python.

## 1. Agentic Core & Orchestration (TypeScript)
*   **Why TypeScript?** The modern ecosystem for autonomous agents and the Model Context Protocol (MCP) is overwhelmingly TypeScript-first. It provides superior static typing for complex LLM schemas.
*   **Engine**: Node.js / `tsx`
*   **MCP SDK**: `@modelcontextprotocol/sdk` for exposing and consuming dynamic tools.

## 2. Hardware & Audio Pipeline (Python)
*   **Why Python?** TypeScript/Node.js struggles natively with low-latency hardware streams and native Windows UI bindings without heavy C++ recompilation. Python handles this flawlessly.
*   **Voice Activity Detection (VAD)**: `silero-vad`
*   **STT**: `faster-whisper`
*   **TTS**: `piper-tts`
*   **Audio I/O**: `sounddevice`
*   **System UI**: `pystray` (Windows System Tray)

## 3. Communication Bridge
*   The Python hardware layer (Listener/Speaker) will communicate with the TypeScript Agent Core via local Inter-Process Communication (IPC) or `stdio` streams (the standard for MCP). 

## 4. Local Processing (Brain)
*   **Ollama (API)**: Manages local inference (`phi3:mini`).
