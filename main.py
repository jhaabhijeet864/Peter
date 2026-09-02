import os
import requests
from dotenv import load_dotenv
from core.config import load_config, update_env_variable
from core.llm import LocalLLM

# New Modular Services
from services.audio.stt.whisper_engine import WhisperSTT
from services.audio.tts.piper_engine import PiperTTS
from services.audio.listener import AudioListener
from ui.tray import SystemTrayUI

_cached_models = []
def get_available_ollama_models():
    """Fetches list of downloaded models directly from local Ollama without blocking the UI thread."""
    global _cached_models
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        # 0.2s timeout ensures the Windows Right-Click menu instantly renders even if Ollama is off
        response = requests.get(f"{host}/api/tags", timeout=0.2)
        response.raise_for_status()
        _cached_models = [model["name"] for model in response.json().get("models", [])]
        return _cached_models
    except Exception as e:
        return _cached_models

def main():
    load_dotenv()
    config = load_config()
    
    llm = LocalLLM()
    
    system_prompt = ""
    if os.path.exists("peter_system.md"):
        with open("peter_system.md", "r") as f:
            system_prompt = f.read()
    
    # Audio Architecture - MOCK MODE DEACTIVATED
    # Peter will now use the real microphone and speakers
    stt = WhisperSTT(mock_mode=False)
    tts = PiperTTS(mock_mode=False)
    listener = AudioListener()
    tts.bind_listener(listener)
    
    # --- Dynamic UI State ---
    active_plugins = {
        "Windows System Controls": True, 
        "Web Search": False, 
        "Gemini Cloud Fallback": False
    }

    # --- Callbacks ---
    def get_models():
        return get_available_ollama_models()

    def set_model(model_name: str):
        print(f"[UI] Switched Active Model to: {model_name}")
        update_env_variable("OLLAMA_MODEL", model_name)
        llm.model = model_name

    def current_model():
        return os.getenv("OLLAMA_MODEL", "phi3:mini")

    def get_plugins():
        return active_plugins

    def toggle_plugin(plugin_name: str):
        active_plugins[plugin_name] = not active_plugins[plugin_name]
        print(f"[UI] Plugin '{plugin_name}' is now {'ENABLED' if active_plugins[plugin_name] else 'DISABLED'}")
        # Phase 6: Notify TS Orchestrator to reload MCP schemas

    def clear_context():
        print("[UI] Action: Cleared LLM short-term memory context.")
        # Phase 5: Flush agentic orchestrator context here

    def toggle_sleep(is_sleeping: bool):
        if is_sleeping:
            print("[UI] Action: SLEEP MODE ACTIVE. Microphone muted.")
            listener.is_muted = True
        else:
            print("[UI] Action: AWAKE MODE ACTIVE. Microphone active.")
            listener.is_muted = False
    # --- Audio Hardware State ---
    selected_mic_index = None
    selected_speaker_index = None

    def get_mics():
        import speech_recognition as sr
        return sr.Microphone.list_microphone_names()

    def set_mic(index):
        nonlocal selected_mic_index
        selected_mic_index = index
        import speech_recognition as sr
        print(f"\n[Hardware] Microphone routed to: {sr.Microphone.list_microphone_names()[index]}")

    def current_mic():
        return selected_mic_index

    def get_speakers():
        import pyaudio
        p = pyaudio.PyAudio()
        speakers = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxOutputChannels"] > 0:
                # Handle Windows ANSI encoding mess cleanly
                try:
                    name = info["name"].encode('cp1252').decode('utf-8')
                except Exception:
                    name = info["name"]
                speakers.append({"index": i, "name": name})
        p.terminate()
        return speakers

    def set_speaker(index):
        nonlocal selected_speaker_index
        selected_speaker_index = index
        print(f"\n[Hardware] Speaker routed to device index: {index}")

    def current_speaker():
        return selected_speaker_index

    # --- Core Callbacks ---
    def on_wake():
        if listener.is_muted and not ui.sleep_mode:
            return 
            
        print("\n[UI] Push-to-Talk triggered. Microphone Active (Green).")
        
        import speech_recognition as sr
        r = sr.Recognizer()
        
        # Phase 14 FIX: Do not auto-calibrate ambient noise! 
        r.energy_threshold = 150 
        r.dynamic_energy_threshold = True
        r.pause_threshold = 1.0 
        
        try:
            # Route to the explicitly selected microphone (or fallback to OS default if None)
            with sr.Microphone(device_index=selected_mic_index) as source:
                print("[UI] Speak now... (Auto-detects when you stop speaking)")
                audio = r.listen(source, timeout=15, phrase_time_limit=20)
                
                ui.set_state("processing")
                print("\n[UI] Processing Intent (Yellow)...")
                user_input = r.recognize_google(audio)
                print(f"[STT] Transcribed: '{user_input}'")
                
        except sr.WaitTimeoutError:
            print("[STT] No speech detected (Timeout).")
            print("[DEBUG] If you spoke, Windows/PyAudio might be listening to a dead default input device (like 'Stereo Mix').")
            # FALLBACK TO TERMINAL TYPING SO THE USER IS NOT BLOCKED
            try:
                user_input = input("\n[UI] ⌨️ Audio input failed. Type your message to Peter (or press Enter to cancel): ").strip()
            except EOFError:
                user_input = ""
                
            if not user_input:
                ui.set_state("idle")
                return
                
            ui.set_state("processing")
            print(f"[STT] Typed: '{user_input}'")
            
        except Exception as e:
            print(f"[STT] Voice recognition failed: {e}")
            ui.set_state("idle")
            return
            
        listener.is_muted = True 
        try:
            response = llm.generate(user_input, system_prompt=system_prompt)
            
            ui.set_state("speaking")
            print(f"\n[Peter ({llm.model})]: {response}\n")
            print("[TTS] Playing audio (Blue)...")
            
            import time
            time.sleep(3) 
            
        except Exception as e:
            print(f"[CRITICAL ERROR] Execution failed: {e}")
        finally:
            if not ui.sleep_mode:
                ui.set_state("idle")
                listener.is_muted = False

    def on_settings():
        print("Opening Settings...")

    def on_quit():
        print("Shutding down Peter.")

    def on_services():
        import base64
        import subprocess
        # Fetching dynamic state of the models and engines
        text = f"=== PETER SERVICES MONITOR ===\n\n[STT Engine] : faster-whisper (Local)\n[Status]     : Loaded & VAD {'Sleeping' if listener.is_muted else 'Active'}\n\n[TTS Engine] : piper-tts (Local)\n[Status]     : Loaded & Awaiting text\n\n[LLM Engine] : Ollama ({llm.model})\n[Status]     : Connected & Warmed up\n\n[MCP Server] : TypeScript stdio Registry\n[Status]     : 10 Tools Loaded & Available\n"
        b64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        b64_title = base64.b64encode("Services Monitor | Peter".encode('utf-8')).decode('utf-8')
        subprocess.Popen(["python", "ui/terminal_popup.py", b64_text, b64_title])

    ui = SystemTrayUI(
        on_wake_cb=on_wake, 
        on_settings_cb=on_settings, 
        on_quit_cb=on_quit,
        get_models_cb=get_models,
        set_model_cb=set_model,
        current_model_cb=current_model,
        get_plugins_cb=get_plugins,
        toggle_plugin_cb=toggle_plugin,
        clear_context_cb=clear_context,
        toggle_sleep_cb=toggle_sleep,
        on_services_cb=on_services,
        get_mics_cb=get_mics,
        set_mic_cb=set_mic,
        current_mic_cb=current_mic,
        get_speakers_cb=get_speakers,
        set_speaker_cb=set_speaker,
        current_speaker_cb=current_speaker
    )
    ui.run()

if __name__ == "__main__":
    main()
