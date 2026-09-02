# Requirements

## 1. Local Audio Pipeline
*   **REQ-1.1**: The system must continuously listen using a lightweight Voice Activity Detection (VAD) to avoid pegging the CPU.
*   **REQ-1.2**: Upon detecting speech, audio must be transcribed via `faster-whisper` (Tiny model).
*   **REQ-1.3**: Upon receiving text from the LLM, the system must synthesize voice via `piper-tts`.
*   **REQ-1.4**: The microphone must mute or ignore input during TTS playback to prevent self-looping.

## 2. Intent & Context Queuing
*   **REQ-2.1**: User commands must be placed into a FIFO queue.
*   **REQ-2.2**: If the LLM is busy, the system must hold the input in the queue and not drop the command or crash.
*   **REQ-2.3**: Context must be strictly capped (e.g., 4096 tokens) discarding the oldest messages (excluding system prompt).

## 3. UI & Control
*   **REQ-3.1**: A Windows System Tray icon must indicate status (Idle, Listening, Thinking, Speaking).
*   **REQ-3.2**: The user must be able to toggle available MCP plugins via the UI.

## 4. MCP System & Actions
*   **REQ-4.1**: Plugins must be hot-loadable from a local directory.
*   **REQ-4.2**: **System Controls**: Must provide toggles for Wi-Fi, Bluetooth, Power Saving, and return Task Manager CPU/RAM stats.
*   **REQ-4.3**: **Vision**: Must use `mss` to capture a screenshot when the user asks "what is on my screen" and feed it to a local vision model or OCR.
*   **REQ-4.4**: **Cloud APIs**: Must include a Gemini API integration that is STRICTLY inactive unless the user uses the specific trigger phrase: *"use gemini api from your closet"*.
*   **REQ-4.5**: **Web Search**: Must be able to query Google for real-time information when required.

## 5. Development Constraints (TDD)
*   **REQ-5.1**: No functional code is written without a corresponding test in `tests/`.
*   **REQ-5.2**: The architecture must separate I/O (Audio, Tray) from Logic (LLM, Queues).
