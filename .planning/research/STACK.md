# Research: Stack

## Summary
The optimal 2026 stack for a low-resource Windows local voice companion balancing performance, offline capability, and low latency.

## 1. Local Processing (Brain)
*   **Ollama (API)**: Manages local inference.
*   **Model**: `phi3:mini` (4-bit quantized) - optimized for low RAM footprint and fast conversational reasoning.

## 2. Audio Pipeline
*   **Voice Activity Detection (VAD)**: `silero-vad` - extremely lightweight, prevents `faster-whisper` from running constantly and spiking CPU.
*   **STT**: `faster-whisper` (Tiny model) - high transcription accuracy on CPU.
*   **TTS**: `piper-tts` - minimal latency, phoneme-based, significantly faster than edge/vosk on CPU.
*   **Audio I/O**: `sounddevice` & `numpy` - low-level, non-blocking audio stream capture and playback.

## 3. Windows Native Integration
*   **System UI**: `pystray` + `Pillow` for the system tray icon and state management.
*   **System Controls**: `psutil` (performance), `pywin32` / `wmi` (power saving, bluetooth, Wi-Fi toggling).
*   **Screen Perception**: `mss` - fastest cross-platform Python screenshot library.

## 4. Architecture Foundation
*   **Asynchronous Engine**: `asyncio` - critical for managing the queue of voice notes, audio streams, and LLM API calls without freezing the tray UI.
*   **Extension Protocol**: Model Context Protocol (MCP) using Python's `importlib` and `inspect` for dynamic capability loading.

## Excluded & Why
*   **PyAudio**: Often requires complex C-bindings and build tools on Windows; `sounddevice` is cleaner via pip.
*   **Vosk / Edge TTS**: Excluded per user requirements (Piper is more controllable locally and doesn't rely on cloud like Edge).
