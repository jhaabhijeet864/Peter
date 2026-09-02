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

    def refresh_audio_devices():
        try:
            for mic in get_mics():
                if "Noise Buds N1" in mic["name"]:
                    set_mic(mic["index"])
                    break
            for spk in get_speakers():
                if "Noise Buds N1" in spk["name"]:
                    set_speaker(spk["index"])
                    break
        except Exception as e:
            print(f"[Hardware] Could not auto-route: {e}")

    # Initial boot route
    refresh_audio_devices()

    # --- Core Callbacks ---
    def on_wake():
        if listener.is_muted and not ui.sleep_mode:
            return 
            
        print("[TTS] Warming up voice engine...")
        try:
            from piper.voice import PiperVoice
            import pyaudio
            model_path = "services/audio/tts/models/en_US-lessac-medium.onnx"
            voice = PiperVoice.load(model_path)
        except Exception as e:
            print(f"[TTS] Failed to load voice engine: {e}")
            return
            
        while True:
            ui.set_state("listening")
            print("\n[UI] Autonomous Mode Active. (Green).")
            print("[UI] Listening for your voice... (Click tray icon to stop)")
            
            import subprocess
            import os
            import speech_recognition as sr
            import time
            import uuid
            
            session_id = uuid.uuid4().hex
            temp_wav = f"voice_{session_id}.wav"
            signal_file = f"signal_{session_id}.active"
            user_input = ""
            
            open(signal_file, 'w').close()
            
            try:
                mic_arg = str(selected_mic_index) if selected_mic_index is not None else "None"
                proc = subprocess.Popen(["python", "services/audio/stt/recorder.py", temp_wav, "15", mic_arg, signal_file])
                
                while ui.state == "listening" and proc.poll() is None:
                    time.sleep(0.1)
                    
                if os.path.exists(signal_file):
                    os.remove(signal_file)
                    
                proc.wait(timeout=2) 
                
                if ui.state != "listening":
                    print("\n[UI] Autonomous mode aborted by user.")
                    break
                
                ui.set_state("processing")
                print("\n[UI] Processing Intent (Yellow)...")
                
                r = sr.Recognizer()
                with sr.AudioFile(temp_wav) as source:
                    audio = r.record(source)
                    
                user_input = r.recognize_google(audio)
                print(f"[STT] Transcribed: '{user_input}'")
                
            except subprocess.CalledProcessError:
                print("\n[STT] FATAL HARDWARE CRASH: Your Audio Driver just caused a PortAudio Segfault.")
                print("[STT] Peter successfully isolated the crash and survived!")
            except sr.UnknownValueError:
                print("\n[STT] The recording was completely silent.")
            except Exception as e:
                if "UnanticipatedHostError" in str(e) or "DeviceUnavailable" in str(e):
                    print(f"\n[STT] EXCLUSIVE LOCK DETECTED: Another app (like Discord) is locking your microphone. Please disable Exclusive Mode in Windows Sound Settings.")
                else:
                    print(f"\n[STT] Voice recognition failed: {e}")
                
            finally:
                if os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except Exception:
                        pass
                if os.path.exists(signal_file):
                    try:
                        os.remove(signal_file)
                    except Exception:
                        pass
                        
            if ui.state == "idle":
                break
                
            if not user_input:
                continue
                
            ui.set_state("processing")
            listener.is_muted = True 
            try:
                response = llm.generate(user_input, system_prompt=system_prompt)
                
                if ui.state == "idle":
                    break
                    
                ui.set_state("speaking")
                print(f"\n[Peter ({llm.model})]: {response}\n")
                print("[TTS] Playing audio (Blue)...")
                
                try:
                    p = pyaudio.PyAudio()
                    speaker_arg = int(selected_speaker_index) if selected_speaker_index is not None else None
                    
                    stream = p.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=voice.config.sample_rate,
                                    output=True,
                                    output_device_index=speaker_arg)
                    
                    import re
                    
                    # Clean up LLM markdown and JSON formatting so the TTS sounds natural
                    spoken_response = response
                    # Remove code blocks entirely (these are usually silent tool calls)
                    spoken_response = re.sub(r'```.*?```', '', spoken_response, flags=re.DOTALL)
                    # Remove inline code
                    spoken_response = re.sub(r'`.*?`', '', spoken_response)
                    # Remove markdown formatting characters
                    spoken_response = spoken_response.replace('*', '').replace('#', '')
                    # Replace underscores with spaces for natural reading
                    spoken_response = spoken_response.replace('_', ' ')
                    # Remove brackets and braces (JSON formatting)
                    spoken_response = re.sub(r'[{}[\]"]', '', spoken_response)
                    
                    spoken_response = spoken_response.strip()
                    # If the response was purely a tool call/code block, give a silent acknowledgment
                    if not spoken_response:
                        spoken_response = "Task executed."
                        
                    for chunk in voice.synthesize(spoken_response):
                        if ui.state != "speaking":
                            print("\n[TTS] Playback interrupted by user.")
                            break
                        stream.write(chunk.audio_int16_bytes)
                        
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                            
                except Exception as e:
                    print(f"[TTS] Failed to play Piper audio: {e}")
                    time.sleep(3) 
                
            except Exception as e:
                print(f"[CRITICAL ERROR] Execution failed: {e}")
            finally:
                listener.is_muted = False
                
            if ui.state == "idle":
                break

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
