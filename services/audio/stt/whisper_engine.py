import numpy as np
import asyncio
from .base import BaseSTT

class WhisperSTT(BaseSTT):
    """
    Implementation of BaseSTT using faster-whisper.
    """
    def __init__(self, model_name="faster-whisper-tiny.en", mock_mode=False):
        self.model_name = model_name
        self.mock_mode = mock_mode
        self.mock_inference_delay = 0.0
        self.model = self._load_model()

    def _load_model(self):
        if self.mock_mode: return None
        return None

    async def transcribe(self, audio_chunk: np.ndarray) -> str:
        if audio_chunk.size == 0:
            return ""

        if np.isnan(audio_chunk).any() or np.isinf(audio_chunk).any():
            raise ValueError("Corrupt audio buffer: detected NaN or Inf values.")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._run_inference, audio_chunk)

    def _run_inference(self, audio_chunk: np.ndarray) -> str:
        if self.mock_mode:
            import time
            if self.mock_inference_delay > 0:
                time.sleep(self.mock_inference_delay)
            return "Simulated transcription text."
        return ""
