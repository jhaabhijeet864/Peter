import os
import requests

class LocalLLM:
    """
    Handles local LLM inference via the Ollama REST API.
    """
    def __init__(self):
        # Read from the local .env configuration
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
        self.api_url = f"{self.host}/api/generate"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Sends the user's prompt to the local Ollama model and returns the response.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "temperature": self.temperature,
            "stream": False
        }
        
        try:
            print(f"[LLM] Connecting to local model '{self.model}' at {self.host}...")
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"[LLM Error] Failed to communicate with local Ollama instance: {e}")
            return "I am currently unable to connect to my local processing core. Please ensure Ollama is running."
