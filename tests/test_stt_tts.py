import pytest
import asyncio
import numpy as np
from services.audio.stt.whisper_engine import WhisperSTT
from services.audio.tts.piper_engine import PiperTTS
from services.audio.listener import AudioListener

@pytest.mark.asyncio
async def test_stt_corrupt_audio_handling():
    stt = WhisperSTT(mock_mode=True)
    result = await stt.transcribe(np.array([], dtype=np.float32))
    assert result == ""
    
    corrupt_audio = np.array([np.nan, np.inf, -np.inf], dtype=np.float32)
    with pytest.raises(ValueError, match="Corrupt audio buffer"):
        await stt.transcribe(corrupt_audio)

@pytest.mark.asyncio
async def test_stt_timeout_enforcement():
    stt = WhisperSTT(mock_mode=True)
    stt.mock_inference_delay = 10.0 
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(stt.transcribe(np.zeros(16000, dtype=np.float32)), timeout=2.0)

@pytest.mark.asyncio
async def test_loopback_prevention_during_tts():
    tts = PiperTTS(mock_mode=True)
    listener = AudioListener()
    
    tts.bind_listener(listener)
    assert listener.is_muted == False
    
    tts_task = asyncio.create_task(tts.speak("Hello, I am Peter."))
    await asyncio.sleep(0.1)
    
    assert listener.is_muted == True, "FATAL: Listener was not muted during TTS playback"
    
    await tts_task
    assert listener.is_muted == False, "FATAL: Listener failed to unmute after TTS finished"
