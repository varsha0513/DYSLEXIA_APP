# Pronunciation Module - Quick Start Guide

## 5-Minute Setup

### 1. Verify Dependencies
```bash
# Check if required packages are installed
pip list | grep -E "pyttsx3|vosk|fastapi"

# If missing, install
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
cd backend
python app.py
```

Expected output:
```
✅ Vosk model loaded
✅ Assistance Module (TTS) ready
✅ Pronunciation Trainer ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### 4. Run a Complete Test

1. Open browser to `http://localhost:5173`
2. Enter age and read a passage
3. On results page, scroll to "Pronunciation Training"
4. Click "Start Training"
5. For each word:
   - Click "🔊 Hear It" - should hear pronunciation
   - Click "🎤 Record" - speak the word
   - View feedback and similarity score
6. Complete training

## Testing the Module Directly

### Test 1: Get Word Pronunciation
```bash
curl -X POST http://localhost:8000/pronunciation/word-audio \
  -F "word=hello" \
  -o hello.wav

# Then play the audio
# On Linux/Mac: afplay hello.wav
# On Windows: powershell -c "[Console]::Beep()"
```

### Test 2: Check Pronunciation (Without Audio)
```bash
curl -X POST http://localhost:8000/pronunciation/word-comparison \
  -F "spoken_word=helo" \
  -F "target_word=hello"
```

Response shows similarity score.

### Test 3: Full Pronunciation Check with Audio

```python
import requests
import wave
import numpy as np

# Step 1: Create a test WAV file
sample_rate = 16000
duration = 2  # seconds
frequency = 440  # Hz

# Generate tone
t = np.linspace(0, duration, sample_rate * duration)
audio_data = np.sin(2 * np.pi * frequency * t)
audio_data = (audio_data * 32767).astype(np.int16)

# Save WAV file
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)      # Mono
    wav_file.setsampwidth(2)       # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

# Step 2: Send to backend
with open('test_audio.wav', 'rb') as f:
    files = {'audio_file': f}
    data = {'word': 'hello'}
    response = requests.post(
        'http://localhost:8000/pronunciation/check',
        files=files,
        data=data
    )

print(response.json())
```

## Common Issues & Solutions

### Issue: Backend doesn't start
```
❌ RuntimeError: Vosk model not found
```
**Solution**: Download Vosk model to correct path:
```bash
cd model
# Download from https://alphacephei.com/vosk/models
unzip vosk-model-small-en-us-0.15.zip
```

### Issue: Microphone permission denied
**Solution**: Chrome/Firefox may require HTTPS. Development:
- Click lock icon in address bar
- Grant microphone permission permanently

### Issue: Backend returns 503 "TTS not available"
**Solution**: Check pyttsx3 installation:
```bash
pip install --upgrade pyttsx3
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

### Issue: No speech recognized
**Solution**: Check audio quality:
1. Ensure clear pronunciation
2. Reduce background noise
3. Check microphone levels
4. Try recording in different environment

## Module Files

### Backend Files
```
backend/
  ├── pronunciation_trainer.py      # Core PronunciationTrainer class
  ├── app.py                        # FastAPI app with endpoints
  ├── text_to_speech.py            # TTS engine
  ├── text_comparison.py           # Word comparison logic
  └── requirements.txt             # Dependencies
```

### Frontend Files
```
frontend/src/components/
  ├── PronunciationTrainingWidget.tsx    # Main component
  ├── PronunciationTrainingWidget.css    # Styling
  ├── ResultsDisplay.tsx                 # Integration point
  └── AssistanceWidget.tsx              # Related component
```

## API Quick Reference

### Generate Pronunciation Audio
```http
POST /pronunciation/word-audio
Content-Type: application/x-www-form-urlencoded

word=pronunciation

→ Response: audio/wav (binary audio data)
```

### Check User Pronunciation
```http
POST /pronunciation/check
Content-Type: multipart/form-data

word=pronunciation
audio_file=<binary WAV file>

→ Response:
{
  "word": "pronunciation",
  "recognized": "pronunciation",
  "is_correct": true,
  "similarity_ratio": 0.95,
  "feedback": "Perfect!",
  "pronunciation_audio": "base64_string"
}
```

### Compare Words (Text Only)
```http
POST /pronunciation/word-comparison
Content-Type: application/x-www-form-urlencoded

spoken_word=pronuncation
target_word=pronunciation

→ Response:
{
  "is_exact_match": false,
  "similarity_ratio": 0.92,
  "confidence": "medium"
}
```

## Customization

### Change TTS Speed
```python
# In app.py, line ~45
tts_engine = DyslexiaAssistanceEngine(
    rate=80,    # Slower (50-300, default 100)
    volume=0.9
)
```

### Change Similarity Threshold
```python
# In pronunciation_trainer.py, check_pronunciation() method
is_correct = is_exact_match or similarity_ratio > 0.90  # Stricter
# or
is_correct = is_exact_match or similarity_ratio > 0.80  # More lenient
```

### Change Maximum Attempts
```python
# In PronunciationTrainingWidget.tsx
if (state.attempts >= 5 && !state.success) {  // Changed from 3 to 5
  // Show skip button
}
```

## Next Steps

1. **Review Documentation**
   - Read `PRONUNCIATION_MODULE_GUIDE.md` for detailed info

2. **Integrate with Assessment Flow**
   - Already integrated! Results auto-show pronunciation training

3. **Customize for Users**
   - Adjust TTS speed for readability level
   - Tune similarity thresholds based on user feedback
   - Add more words to practice

4. **Monitor Usage**
   - Track which words users struggle with
   - Analyze pronunciation patterns
   - Adjust recommendations

## Support

For issues or questions:
1. Check browser console (F12) for frontend errors
2. Check terminal output for backend errors
3. Review logs in PRONUNCIATION_MODULE_GUIDE.md
4. Check GitHub issues or documentation

---

**Status**: ✅ Ready to Use  
**Version**: 1.0.0
