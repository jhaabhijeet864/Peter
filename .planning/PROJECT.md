# Peter - Windows Voice Companion

## What This Is
Peter is a lightweight, low-resource voice companion and digital butler for Windows. It runs fully locally using optimized open-weights models (Ollama/Phi-3, faster-whisper, piper-tts) while maintaining a minimal system footprint. Peter is designed for real-time conversational interaction, queuing inputs to prevent context jamming, and offering robust local system controls alongside a highly extensible MCP plugin architecture.

## Core Value
Providing a highly responsive, privacy-first local AI butler that can interact conversationally, perceive the desktop environment, and execute complex system or web tasks without relying on cloud infrastructure by default.

## Requirements

### Validated
- ✓ System Tray presence and basic UI controls.
- ✓ Base local LLM integration via Ollama REST API.
- ✓ Scalable MCP server foundation with dynamic plugin loading.
- ✓ Configurable guardrails blocking destructive commands.

### Active
- [ ] **Voice Pipeline**: Implement `faster-whisper` for STT and `piper-tts` for TTS (strictly no Vosk or Edge TTS).
- [ ] **Wake Word System**: Continuous listening for "Peter", triggering a greeting and activation.
- [ ] **Context & Queue Management**: Process voice notes sequentially; queue additional notes so the agent does not jam.
- [ ] **Vision/Screen Awareness**: Ability to take screenshots and process them locally to understand the user's screen state.
- [ ] **System Controls**: Tools to check and toggle Internet, Wi-Fi, Bluetooth, Power Saving Mode, and System Performance (Task Manager).
- [ ] **UI-Configurable MCP**: Add MCP servers from different accounts and configure them directly via the System Tray UI.
- [ ] **Cloud/Fallback Integration**: 
  - [ ] Google Search access.
  - [ ] Gemini API integration (strictly inactive unless triggered by specific phrases like "use gemini api from your closet").
  - [ ] ElevenLabs API for voice modulation (inactive by default).
- [ ] **TDD & Architecture**: 
  - [ ] Reshape directory structure for Test-Driven Development.
  - [ ] Implement proper structural checks and test suites before any further execution coding.

### Out of Scope
- Heavy continuous screen recording (impacts low-resource constraint).
- Default reliance on cloud APIs for core conversational features.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Test-Driven Development** | Ensures structural integrity and stability before complex logic is wired. | — Pending |
| **Local-First Audio Stack** | `piper-tts` and `faster-whisper` provide the best balance of speed and offline capability. | — Pending |
| **Context Queuing** | Small models fail on massive context dumps. Queuing inputs prevents hallucinations and jams. | — Pending |

## Evolution
This document evolves at phase transitions and milestone boundaries.
---
*Last updated: 2026-09-02 after initialization*
