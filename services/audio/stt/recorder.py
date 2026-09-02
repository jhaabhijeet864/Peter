import sys
import sounddevice as sd
import wave

def record(output_file, duration=6):
    fs = 16000
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    record(sys.argv[1], int(sys.argv[2]))
