# Project Roadmap

This project uses Fine granularity (many focused phases) and enforces Test-Driven Development (TDD) for every step.

## Phase 1: Foundation & TDD Scaffold
- **Goal**: Establish the async architecture, test suite, and logging.
- **Deliverables**: `pytest` configuration, baseline async event loop, and guardrails module with tests.

## Phase 2: Audio Listener & VAD
- **Goal**: Implement non-blocking audio capture with Voice Activity Detection.
- **Deliverables**: `sounddevice` capture stream, `silero-vad` integration, tests for speech detection accuracy and CPU usage.

## Phase 3: The Voice Queuing System
- **Goal**: Build the FIFO queue that prevents LLM jamming.
- **Deliverables**: Thread-safe Async Queue, unit tests proving commands are held while the processor is busy.

## Phase 4: STT & TTS Integration
- **Goal**: Connect the models for processing audio.
- **Deliverables**: `faster-whisper` transcription module, `piper-tts` synthesis module, and audio-loopback prevention (muting during speaking).

## Phase 5: Local LLM Brain
- **Goal**: Connect the queuing system to the local Ollama instance.
- **Deliverables**: `phi3:mini` integration, context token limitation window, prompt injection prevention.

## Phase 6: MCP Plugin Architecture
- **Goal**: Build the dynamic extension layer.
- **Deliverables**: Plugin loader, integration with the LLM system prompt, isolated plugin tests.

## Phase 7: System Operations Plugin
- **Goal**: Enable desktop control.
- **Deliverables**: MCP tool for Wi-Fi, Bluetooth, Power Saving, and Task Manager statistics. 

## Phase 8: Vision & Perception Plugin
- **Goal**: Allow Peter to see the screen.
- **Deliverables**: `mss` screenshot tool, local OCR/Vision preprocessing before sending to the LLM.

## Phase 9: Cloud Fallback Plugin
- **Goal**: Integrate external APIs safely.
- **Deliverables**: Google search MCP, Gemini API (with strict trigger-phrase activation test), ElevenLabs MCP (default off).

## Phase 10: System Tray UI Integration
- **Goal**: Bind the backend to the Windows UI.
- **Deliverables**: `pystray` icon, state color changes, context menu for plugin toggling.

## Phase 11: End-to-End Polish
- **Goal**: Final integration and latency optimization.
- **Deliverables**: Comprehensive E2E tests, packaging, and final documentation.
