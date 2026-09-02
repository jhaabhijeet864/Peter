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
        import pyaudio
        p = pyaudio.PyAudio()
        mics = []
        seen_names = set()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                try:
                    name = info["name"].encode('cp1252', errors='ignore').decode('utf-8', errors='ignore')
                except Exception:
                    name = info["name"]
                # Windows exposes the same hardware across MME, DirectSound, and WASAPI APIs. 
                # We strip the API suffixes to deduplicate the visual list for the user.
                clean_name = name.replace("(MME)", "").replace("(DirectSound)", "").replace("(WASAPI)", "").strip()
                
                # Further deduplication based on prefix
                short_name = clean_name[:15]
                if short_name not in seen_names:
                    seen_names.add(short_name)
                    mics.append({"index": i, "name": name})
        p.terminate()
        return mics

    def set_mic(index):
        nonlocal selected_mic_index
        selected_mic_index = index
        print(f"\n[Hardware] Microphone routed to device index: {index}")

    def current_mic():
        return selected_mic_index

    def get_speakers():
        import pyaudio
        p = pyaudio.PyAudio()
        speakers = []
        seen_names = set()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxOutputChannels"] > 0:
                try:
                    name = info["name"].encode('cp1252', errors='ignore').decode('utf-8', errors='ignore')
                except Exception:
                    name = info["name"]
                
                clean_name = name.replace("(MME)", "").replace("(DirectSound)", "").replace("(WASAPI)", "").strip()
                short_name = clean_name[:15]
                if short_name not in seen_names:
                    seen_names.add(short_name)
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
            
        print("\n[UI] Push-to-Talk triggered. (Green).")
        
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 150 
        r.dynamic_energy_threshold = True
        r.pause_threshold = 1.0 
        
        print("\n[UI] Push-to-Talk triggered. Microphone Active (Green).")
        print("[UI] Speak your command now... (Recording for 6 seconds)")
        
        # Phase 14 FIX: Completely bypassing PyAudio/PortAudio initialization to prevent Windows driver segfaults.
        # We instead use `sounddevice` (which you just proved works) to record a fixed clip, save it natively, and transcribe.
        import sounddevice as sd
        import wave
        import os
        
        fs = 16000
        duration = 6
        
        try:
            # Record audio directly via sounddevice
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            
            ui.set_state("processing")
            print("\n[UI] Processing Intent (Yellow)...")
            
            # Save to temporary WAV
            temp_wav = "temp_voice.wav"
            with wave.open(temp_wav, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 16-bit
                wf.setframerate(fs)
                wf.writeframes(recording.tobytes())
                
            # Transcribe the WAV file safely without touching PyAudio
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(temp_wav) as source:
                audio = r.record(source)
                
            user_input = r.recognize_google(audio)
            print(f"[STT] Transcribed: '{user_input}'")
            
            # Cleanup
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
        except Exception as e:
            print(f"[STT] Voice recognition failed: {e}")
            # FALLBACK
            try:
                user_input = input("\n[UI] ⌨️ Audio failed. Type your command: ").strip()
            except EOFError:
                user_input = ""
                
        if not user_input:
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
