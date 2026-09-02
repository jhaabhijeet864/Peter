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
from mcp.server import MCPServer

def get_available_ollama_models():
    """Fetches list of downloaded models directly from local Ollama."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        response = requests.get(f"{host}/api/tags", timeout=2)
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        print(f"[Ollama Error] Failed to fetch models: {e}")
        return []

def main():
    load_dotenv()
    config = load_config()
    
    llm = LocalLLM()
    
    system_prompt = ""
    if os.path.exists("peter_system.md"):
        with open("peter_system.md", "r") as f:
            system_prompt = f.read()
    
    # Audio Architecture
    stt = WhisperSTT(mock_mode=True)
    tts = PiperTTS(mock_mode=True)
    listener = AudioListener()
    tts.bind_listener(listener)
    
    mcp = MCPServer("local_os_operations", plugins_package="mcp.plugins")
    
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

    def on_wake():
        print("\n[UI] Wake triggered. Walkie-talkie mode active...")
        user_input = "Hello Peter, what is your status?"
        print(f"[STT] Heard: {user_input}")
        
        listener.is_muted = True 
        
        response = llm.generate(user_input, system_prompt=system_prompt)
        print(f"\n[Peter ({llm.model})]: {response}\n")
        
        print("[TTS] Playing audio...")

    def on_settings():
        print("Opening Settings...")

    def on_quit():
        print("Shutting down Peter.")

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
        toggle_sleep_cb=toggle_sleep
    )
    ui.run()

if __name__ == "__main__":
    main()
