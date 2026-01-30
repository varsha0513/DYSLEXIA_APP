import sounddevice as sd
import queue
import json
import os
from vosk import Model, KaldiRecognizer

# Load model
model_path = "../model/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    print("Please download the model first")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Start microphone
with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback):

    print("🎤 Start reading... Press Ctrl+C to stop")

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print("Recognized:", result["text"])
