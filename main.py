import os
from dotenv import load_dotenv
from core.config import load_config
from core.llm import LocalLLM
from ui.tray import SystemTrayUI
from audio.pipeline import AudioPipeline
from mcp.server import MCPServer

def main():
    # 1. Load Environment Configuration
    load_dotenv()
    config = load_config()
    
    # 2. Initialize Local LLM Backend (Ollama)
    llm = LocalLLM()
    
    # Load Persona / System Prompt
    system_prompt = ""
    if os.path.exists("peter_system.md"):
        with open("peter_system.md", "r") as f:
            system_prompt = f.read()
    
    # 3. Initialize Audio Pipeline
    audio_cfg = config.get("audio_pipeline", {})
    audio = AudioPipeline(
        stt_model_name=os.getenv("STT_MODEL", audio_cfg.get("stt", "faster-whisper-tiny.en")),
        tts_model_name=os.getenv("TTS_MODEL", audio_cfg.get("tts", "piper-tts (en_US-lessac-medium)"))
    )
    
    # 4. Initialize Dynamic MCP Server
    mcp = MCPServer("local_os_operations", plugins_package="mcp.plugins")
    
    # 5. Define UI Callbacks
    def on_wake():
        print("\n[UI] Wake triggered. Listening...")
        
        # For now, we simulate STT input until the audio pipeline is fully wired
        user_input = "Hello Peter, what is your status?"
        print(f"[STT Simulation] Heard: {user_input}")
        
        # Route to Local LLM
        response = llm.generate(user_input, system_prompt=system_prompt)
        print(f"\n[Peter]: {response}\n")
        
        # Output via TTS
        audio.speak(response)

    def on_settings():
        print("Opening Settings...")

    def on_quit():
        print("Shutting down Peter.")

    # 6. Initialize System Tray UI
    ui = SystemTrayUI(
        on_wake_cb=on_wake,
        on_settings_cb=on_settings,
        on_quit_cb=on_quit
    )
    
    print("Starting Peter System Tray UI...")
    ui.run()

if __name__ == "__main__":
    main()
