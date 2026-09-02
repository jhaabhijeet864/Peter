import asyncio
from .base import BaseTTS

class PiperTTS(BaseTTS):
    """
    Implementation of BaseTTS using piper-tts.
    """
    def __init__(self, model_name="piper-tts (en_US-lessac-medium)", mock_mode=False):
        self.model_name = model_name
        self.mock_mode = mock_mode
        self.listener = None
        self.model = self._load_model()

    def _load_model(self):
        if self.mock_mode: return None
        return None

    def bind_listener(self, listener):
        self.listener = listener

    async def speak(self, text: str):
        if self.listener:
            self.listener.is_muted = True

        try:
            if self.mock_mode:
                await asyncio.sleep(0.5) 
            else:
                pass
        finally:
            if self.listener:
                self.listener.is_muted = False
