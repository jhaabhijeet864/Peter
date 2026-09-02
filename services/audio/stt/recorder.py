import sys
import os
import time
import wave
import sounddevice as sd
import numpy as np

def record(output_file, max_duration=15, device_index=None, signal_file=None):
    fs = 16000
    device = int(device_index) if device_index is not None and device_index != 'None' else None
    
    audio_frames = []
    
    def callback(indata, frames, time_info, status):
        audio_frames.append(indata.copy())
        
    try:
        stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16', device=device, callback=callback)
        with stream:
            start_time = time.time()
            while time.time() - start_time < max_duration:
                time.sleep(0.1)
                if signal_file and not os.path.exists(signal_file):
                    break # User clicked stop!
    except Exception as e:
        print(f'Recorder error: {e}')
        sys.exit(1)
        
    if audio_frames:
        recording = np.concatenate(audio_frames)
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    device_idx = sys.argv[3] if len(sys.argv) > 3 else 'None'
    signal_file = sys.argv[4] if len(sys.argv) > 4 else None
    record(sys.argv[1], int(sys.argv[2]), device_idx, signal_file)
