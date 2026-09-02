# Research: Pitfalls & Gotchas

## 1. CPU & Memory Spikes
*   **The VAD Trap**: Running `faster-whisper` continuously on raw microphone input will consume 100% CPU on low-resource machines. **Mitigation**: We *must* use a Voice Activity Detection (VAD) model to gate the STT. Only send audio segments containing speech to `faster-whisper`.
*   **LLM Jamming**: If the user gives multiple commands quickly, the local model will overlap and crash. **Mitigation**: The strict queuing system designed in the architecture.

## 2. Windows Privileges
*   **Hardware Toggles**: Toggling Wi-Fi or Bluetooth programmatically on modern Windows often requires Administrator privileges. **Mitigation**: The guardrail system must gracefully handle `Access Denied` errors. If Peter requires Admin, the `start.bat` must request elevation.

## 3. Audio Loopback (Hearing Itself)
*   **Echo Cancellation**: When Peter speaks, the microphone will pick up its own TTS output, causing it to transcribe and loop its own words. **Mitigation**: The `Listener` must be explicitly paused or muted during `piper-tts` playback, or a robust Echo Cancellation layer must be applied (pausing is safer for low-resource).

## 4. Asynchronous Tray UI
*   `pystray` runs a blocking event loop. If not handled correctly, tying it to a blocking LLM call will freeze the Windows taskbar icon. **Mitigation**: The `pystray` loop must run in a separate daemon thread while the main thread handles `asyncio` logic.
