from abc import ABC, abstractmethod
import numpy as np

class BaseSTT(ABC):
    """
    Abstract Base Class for Speech-to-Text Engines.
    Ensures that future STT models (e.g., local, cloud fallback) 
    must implement the exact same interface.
    """
    @abstractmethod
    async def transcribe(self, audio_chunk: np.ndarray) -> str:
        pass
