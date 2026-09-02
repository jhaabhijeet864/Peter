from .stt import STTModel
from .tts import TTSModel

class AudioPipeline:
    def __init__(self, stt_model_name, tts_model_name):
        self.stt = STTModel(stt_model_name)
        self.tts = TTSModel(tts_model_name)

    def listen_and_transcribe(self):
        return self.stt.listen()

    def speak(self, text):
        self.tts.speak(text)
