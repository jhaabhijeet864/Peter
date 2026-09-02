import pytest
import numpy as np
from services.audio.listener import VADFilter

def test_vad_filter_silence():
    vad = VADFilter(mock_mode=True)
    silent_chunk = np.zeros(512, dtype=np.float32)
    assert vad.is_speech(silent_chunk) == False

def test_vad_filter_speech():
    vad = VADFilter(mock_mode=True)
    loud_chunk = np.random.uniform(-0.8, 0.8, 512).astype(np.float32)
    assert vad.is_speech(loud_chunk) == True
