import sys
import sounddevice as sd
import wave

def record(output_file, duration=6, device_index=None):
    fs = 16000
    device = int(device_index) if device_index is not None and device_index != 'None' else None
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=device)
    sd.wait()
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    device_idx = sys.argv[3] if len(sys.argv) > 3 else 'None'
    record(sys.argv[1], int(sys.argv[2]), device_idx)
