from abc import ABC, abstractmethod

class BaseTTS(ABC):
    """
    Abstract Base Class for Text-to-Speech Engines.
    Ensures modularity for future add-on models (e.g., ElevenLabs).
    """
    @abstractmethod
    def bind_listener(self, listener):
        pass

    @abstractmethod
    async def speak(self, text: str):
        pass
