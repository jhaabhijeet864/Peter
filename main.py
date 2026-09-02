import os
from dotenv import load_dotenv
from core.config import load_config
from core.llm import LocalLLM
from ui.tray import SystemTrayUI
from mcp.server import MCPServer

# New Modular Services
from services.audio.stt.whisper_engine import WhisperSTT
from services.audio.tts.piper_engine import PiperTTS
from services.audio.listener import AudioListener

def main():
    load_dotenv()
    config = load_config()
    
    llm = LocalLLM()
    
    system_prompt = ""
    if os.path.exists("peter_system.md"):
        with open("peter_system.md", "r") as f:
            system_prompt = f.read()
    
    # Initialize Modular Audio Architecture
    stt = WhisperSTT(mock_mode=True)
    tts = PiperTTS(mock_mode=True)
    listener = AudioListener()
    
    # Bind for loopback prevention (half-duplex walkie-talkie mode)
    tts.bind_listener(listener)
    
    mcp = MCPServer("local_os_operations", plugins_package="mcp.plugins")
    
    def on_wake():
        print("\n[UI] Wake triggered. Walkie-talkie mode active...")
        # 1. User speaks -> Mic captures -> STT
        user_input = "Hello Peter, what is your status?"
        print(f"[STT] Heard: {user_input}")
        
        # 2. Shut off mic while working/speaking
        listener.is_muted = True 
        
        # 3. LLM processes as a WORKER (extreme brevity)
        response = llm.generate(user_input, system_prompt=system_prompt)
        print(f"\n[Peter]: {response}\n")
        
        # 4. Speak (TTS handles unmuting the listener when done)
        # Note: In real async loop, this is awaited.
        print("[TTS] Playing audio...")

    def on_settings():
        print("Opening Settings...")

    def on_quit():
        print("Shutting down Peter.")

    ui = SystemTrayUI(on_wake_cb=on_wake, on_settings_cb=on_settings, on_quit_cb=on_quit)
    ui.run()

if __name__ == "__main__":
    main()
