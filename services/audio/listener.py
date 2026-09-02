import numpy as np
import asyncio

class VADFilter:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode

    def is_speech(self, audio_chunk: np.ndarray, threshold: float = 0.5) -> bool:
        if self.mock_mode:
            energy = np.mean(np.abs(audio_chunk))
            return energy > 0.1
        return False

class AudioListener:
    def __init__(self, sample_rate=16000, chunk_size=512):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.vad = VADFilter()
        self.is_listening = False
        self.is_muted = False
        self.audio_buffer = []

    def audio_callback(self, indata, frames, time, status):
        # Guardrail: Absolute silence enforcement (Mic shuts off completely during TTS)
        if self.is_muted:
            self.audio_buffer.clear()
            return
            
        chunk = indata[:, 0]
        
        if self.vad.is_speech(chunk):
            self.audio_buffer.append(chunk.copy())
        else:
            if len(self.audio_buffer) > 5:
                self._dispatch_utterance()
                
    def _dispatch_utterance(self):
        self.audio_buffer = []

    async def start(self):
        self.is_listening = True

    def stop(self):
        self.is_listening = False
