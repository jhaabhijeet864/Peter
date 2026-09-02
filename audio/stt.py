class STTModel:
    def __init__(self, model_name="faster-whisper-tiny.en"):
        self.model_name = model_name
        self.model = self._load_model()

    def _load_model(self):
        print(f"Loading STT model: {self.model_name}")
        return None

    def listen(self):
        # Implementation for capturing and transcribing audio
        pass
