# Pronunciation Assistance Module - Complete Documentation

## Overview

The Pronunciation Assistance Module is an interactive learning system integrated into the Dyslexia Support Application. It helps users master the correct pronunciation of words they misread during assessments.

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PronunciationTrainingWidget                         │   │
│  │  - UI for interactive pronunciation training         │   │
│  │  - Recording management                              │   │
│  │  - Audio playback and feedback display               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕↕↕ HTTP/JSON ↕↕↕
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (Python)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PronunciationTrainer                                │   │
│  │  - speak_word(): TTS pronunciation generation       │   │
│  │  - listen_word(): Speech recognition with Vosk      │   │
│  │  - check_pronunciation(): Word comparison logic      │   │
│  │  - pronunciation_training(): Complete workflow       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                       │   │
│  │  - POST /pronunciation/word-audio                    │   │
│  │  - POST /pronunciation/check                         │   │
│  │  - POST /pronunciation/word-comparison               │   │
│  │  - POST /pronunciation/batch-check                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕↕↕ ↕↕↕
┌─────────────────────────────────────────────────────────────┐
│              Supporting Systems                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   pyttsx3    │  │    Vosk      │  │ Text Compare │      │
│  │   (TTS)      │  │   (Speech    │  │   (Analysis) │      │
│  │              │  │ Recognition) │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Module Features

### 1. Text-to-Speech (TTS) - Word Pronunciation
**Purpose**: Pronounce the correct word for user to hear

**Function**: `speak_word(word: str, rate: int = 100)`

**Process**:
- Takes a target word as input
- Uses pyttsx3 to generate natural speech
- Returns audio bytes and base64-encoded audio
- Executed via subprocess for isolation

**Features**:
- Configurable speech rate (50-300 WPM)
- MP3/WAV output support
- Offline operation (no internet required)
- Natural pronunciation quality

### 2. Speech Recognition - User Attempt
**Purpose**: Capture and convert user's spoken word to text

**Function**: `listen_word(audio_bytes: bytes, duration_ms: int = 5000)`

**Process**:
- Receives raw WAV audio from frontend
- Parses audio file format and properties
- Feeds audio to Vosk speech recognition engine
- Extracts recognized text

**Features**:
- 16kHz audio support
- Robust handling of noise and accents
- Real-time recognition feedback
- Accurate word-level detection

### 3. Pronunciation Comparison - Word Analysis
**Purpose**: Compare recognized word with target word

**Function**: `check_pronunciation(recognized_word: str, correct_word: str)`

**Process**:
1. Normalizes both words (lowercase, trim)
2. Calculates exact match
3. Computes similarity ratio using difflib
4. Determines if pronunciation is correct

**Matching Rules**:
```
- Exact Match: 100% correctness
- Similarity > 0.85: Accepted as correct (allows minor variations)
- Similarity 0.70-0.85: Close attempt, retry encouraged
- Similarity < 0.70: Significant difference, retry recommended
```

**Returns**:
```json
{
  "is_exact_match": boolean,
  "similarity_ratio": 0.0-1.0,
  "is_correct": boolean,
  "feedback": "Feedback message for user"
}
```

### 4. Training Orchestration - Workflow Management
**Purpose**: Manage complete pronunciation training session

**Function**: `pronunciation_training(word: str, user_audio_bytes: bytes)`

**Workflow**:
```
1. Pronounce the word (TTS)
   ↓
2. Listen to user attempt (Vosk)
   ↓
3. Compare with target (difflib)
   ↓
4. Provide feedback
   ↓
5. Return results with audio and metrics
```

**Returns**:
```json
{
  "word": "target_word",
  "is_correct": true/false,
  "recognized": "what was recognized",
  "similarity_ratio": 0.95,
  "feedback": "Great job!",
  "pronunciation_audio": "base64_audio_data",
  "attempt_details": {
    "raw_recognized": "raw_text",
    "exact_match": true/false,
    "similarity_ratio": 0.95
  }
}
```

## API Endpoints

### 1. Get Word Pronunciation
**Endpoint**: `POST /pronunciation/word-audio`

**Request**:
```form
word: string (required) - Word to pronounce
```

**Response**:
```
Audio file (WAV format)
Content-Type: audio/wav
```

**Example**:
```bash
curl -X POST http://localhost:8000/pronunciation/word-audio \
  -F "word=pronunciation"
```

**Use Case**: "Hear it" button - user clicks to hear correct pronunciation

---

### 2. Check Pronunciation
**Endpoint**: `POST /pronunciation/check`

**Request**:
```form
word: string (required) - Target word
audio_file: file (required) - WAV audio of user's attempt
```

**Response**:
```json
{
  "word": "pronunciation",
  "recognized": "pronuncation",
  "correct": "pronunciation",
  "is_correct": false,
  "similarity_ratio": 0.92,
  "feedback": "Close! You said 'pronuncation' but ...",
  "pronunciation_audio": "base64_string",
  "raw_recognized": "pronuncation",
  "exact_match": false
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/pronunciation/check \
  -F "word=pronunciation" \
  -F "audio_file=@user_audio.wav"
```

**Use Case**: Main pronunciation check - user records attempt and gets feedback

---

### 3. Compare Words (Text-Only)
**Endpoint**: `POST /pronunciation/word-comparison`

**Request**:
```form
spoken_word: string (required) - User's spoken word
target_word: string (required) - Correct word
```

**Response**:
```json
{
  "spoken": "pronuncation",
  "target": "pronunciation",
  "is_exact_match": false,
  "similarity_ratio": 0.92,
  "confidence": "medium",
  "details": {
    "spoken": "pronuncation",
    "target": "pronunciation",
    "spoken_normalized": "pronuncation",
    "target_normalized": "pronunciation"
  }
}
```

**Use Case**: Word comparison without audio processing (testing/debugging)

---

### 4. Batch Word Check
**Endpoint**: `POST /pronunciation/batch-check`

**Request**:
```form
words: string (required) - JSON array of words
audio_files: files (optional) - Multiple audio files
```

**Response**:
```json
{
  "total_words": 5,
  "words": [
    {
      "word": "pronunciation",
      "status": "ready",
      "feedback": "Ready to practice pronunciation of 'pronunciation'"
    },
    // ... more words
  ]
}
```

**Use Case**: Batch preparation for multiple words

---

## Frontend Integration

### PronunciationTrainingWidget Component

**Props**:
```typescript
interface PronunciationTrainingWidgetProps {
  words: string[];              // Words to practice
  onComplete?: (results: TrainingResult[]) => void;  // Completion callback
}

interface TrainingResult {
  word: string;
  success: boolean;
  attempts: number;
  feedback: string;
}
```

**Usage in ResultsDisplay**:
```typescript
<PronunciationTrainingWidget
  words={[
    ...results.assistance.wrong_words.map(([_, correct]) => correct),
    ...results.assistance.missing_words,
  ]}
  onComplete={(results) => {
    console.log('Training complete:', results);
  }}
/>
```

**User Workflow**:
1. Assessment completes with errors detected
2. Results page shows misread words
3. User can click "Start Training" on PronunciationTrainingWidget
4. For each word:
   - Click "🔊 Hear It" to listen to correct pronunciation
   - Click "🎤 Record" and speak the word
   - See similarity score and feedback
   - Continue until correct or max attempts reached
5. Session summary shows mastered words

### Audio Recording

**Browser Requirements**:
- Modern browser with Web Audio API
- Microphone access permission
- HTTPS recommended (required for some browsers)

**Format Conversion**:
```
WebM (browser default) → WAV (backend required)
  ↓
Convert using AudioContext
  ↓
PCM to int16 format
  ↓
Add WAV header
  ↓
Send to backend
```

## Backend Implementation Details

### PronunciationTrainer Class

**Initialization**:
```python
from pronunciation_trainer import PronunciationTrainer
from vosk import Model
from text_to_speech import DyslexiaAssistanceEngine

model = Model("../model/vosk-model-small-en-us-0.15")
tts_engine = DyslexiaAssistanceEngine(rate=100, volume=0.9)
trainer = PronunciationTrainer(vosk_model=model, tts_engine=tts_engine)
```

**Core Methods**:

1. **speak_word()**
   ```python
   audio_bytes, audio_base64 = trainer.speak_word("pronunciation")
   # Returns: (bytes, base64_string)
   ```

2. **listen_word()**
   ```python
   recognized = trainer.listen_word(audio_bytes)
   # Returns: "pronunciation" (recognized text)
   ```

3. **check_pronunciation()**
   ```python
   result = trainer.check_pronunciation("pronuncation", "pronunciation")
   # Returns: {
   #   "is_correct": False,
   #   "similarity_ratio": 0.92,
   #   "feedback": "..."
   # }
   ```

4. **pronunciation_training()**
   ```python
   result = trainer.pronunciation_training("pronunciation", audio_bytes)
   # Returns: Complete session result with all details
   ```

### Integration with FastAPI

**In app.py**:
```python
from pronunciation_trainer import PronunciationTrainer

# Initialize
pronunciation_trainer = PronunciationTrainer(
    vosk_model=model,
    tts_engine=tts_engine
)

# In endpoint
@app.post("/pronunciation/check")
async def check_pronunciation(word: str, audio_file: UploadFile):
    audio_bytes = await audio_file.read()
    result = pronunciation_trainer.pronunciation_training(word, audio_bytes)
    return result
```

## Word Comparison Algorithm

### Normalization
```python
word = "Pronunciation"
normalized = word.lower().strip()  # "pronunciation"
```

### Similarity Calculation
Uses Python's `difflib.SequenceMatcher` for character-level comparison:

```
Target:     "pronunciation"
Recognized: "pronuncation"
Match:      P R O N U N C A T I O N
            P R O N U N C - A T I O N
Ratio:      12/13 ≈ 0.92 (92%)
```

### Decision Logic
```python
if recognized == correct:
    is_correct = True  # Exact match
elif similarity > 0.85:
    is_correct = True  # Accept as correct
elif similarity > 0.70:
    is_correct = False  # Encourage retry
else:
    is_correct = False  # Suggest more practice
```

## Error Handling

### Frontend Errors

1. **Microphone Access Denied**
   - Message: "Microphone access denied"
   - Solution: Check browser permissions, grant access

2. **Audio Processing Failed**
   - Message: "Failed to analyze"
   - Solution: Ensure audio is clear, try recording again

3. **Backend Connection Failed**
   - Message: Shows connection error
   - Solution: Ensure backend server is running

### Backend Errors

1. **Empty Audio File**
   - Status: 400
   - Message: "Audio file is empty"

2. **TTS Engine Not Available**
   - Status: 503
   - Message: "Pronunciation assistance not available"

3. **Vosk Recognition Failure**
   - Returns: Empty string
   - Handled: User is prompted to try again

## Configuration

### TTS Settings
```python
tts_engine = DyslexiaAssistanceEngine(
    rate=100,        # Speed: 50-300 (100 = normal)
    volume=0.9       # Volume: 0.0-1.0
)
```

### Trainer Settings
```python
trainer = PronunciationTrainer(
    vosk_model=model,
    tts_engine=tts_engine
    # max_attempts: 3 (default)
)
```

### Similarity Threshold
```python
# In check_pronunciation()
is_correct = (is_exact_match or similarity_ratio > 0.85)
# Adjust 0.85 threshold as needed
```

## Performance Metrics

### Typical Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| TTS Generation | 1-2s | Subprocess overhead |
| Vosk Recognition | 0.5-1.5s | Depends on audio length |
| Comparison | <10ms | Fast similarity calculation |
| Total Attempt | 2-4s | User-to-feedback time |

### System Requirements

- **Backend**: Python 3.7+, ~200MB RAM per request
- **Frontend**: Modern browser (Chrome, Firefox, Edge, Safari)
- **Network**: 1-2 Mbps sufficient
- **Microphone**: Standard computer/device microphone

## Testing

### Manual Testing Checklist

- [ ] "Hear it" button plays correct pronunciation
- [ ] Recording starts when button clicked
- [ ] Microphone access dialog appears
- [ ] Microphone recording indicator shows
- [ ] Stop button works
- [ ] Audio is processed and sent
- [ ] Feedback displays correctly
- [ ] Similarity score shows
- [ ] "Try Again" button resets state
- [ ] "Next Word" button proceeds
- [ ] All words completed successfully
- [ ] Session summary displays

### Test Cases

**Case 1: Perfect Pronunciation**
```
Target: "pronunciation"
User says: "pronunciation" (clearly)
Expected: is_correct = True, feedback = "Perfect!"
```

**Case 2: Minor Mispronunciation**
```
Target: "pronunciation"
User says: "pronuncation" (missing 'i')
Expected: is_correct = True, feedback = "Close enough!"
similarity >= 0.85
```

**Case 3: Significant Error**
```
Target: "pronunciation"
User says: "pronon" (very different)
Expected: is_correct = False, feedback = "Try again"
similarity < 0.85
```

**Case 4: No Speech**
```
Target: "pronunciation"
User provides: Silent audio
Expected: recognized = "", suggest retry
```

## Troubleshooting

### Issue: No Audio Playback
**Symptoms**: "Hear it" button does nothing

**Solutions**:
1. Check browser volume unmuted
2. Verify backend TTS engine running: `print(tts_engine)`
3. Check browser console for errors
4. Try different browser

### Issue: Microphone Not Working
**Symptoms**: "Microphone access denied"

**Solutions**:
1. Grant microphone permission in browser settings
2. Check OS microphone permissions
3. Restart browser
4. Try different browser

### Issue: Backend Errors
**Symptoms**: 500 errors in backend logs

**Solutions**:
1. Ensure Vosk model path is correct
2. Check pyttsx3 installation: `pip install pyttsx3`
3. Verify audio file format is WAV
4. Check server logs for detailed errors

## Dependencies

**Backend**:
- fastapi==0.104.1
- pyttsx3>=2.90
- vosk==0.3.45
- sounddevice==0.4.5
- numpy>=1.19.0
- pydantic==2.5.0

**Frontend**:
- React 18+
- TypeScript 4.5+
- Web Audio API (builtin)

**System**:
- Python 3.7+
- Modern web browser

## Future Enhancements

1. **Accent Recognition**: Identify and support different English accents
2. **Progress Tracking**: Store user pronunciation history
3. **Difficulty Levels**: Adjust word complexity based on performance
4. **Phonetic Breakdown**: Show phonetic spelling and pronunciation guide
5. **Peer Comparison**: Compare user pronunciation to native speaker
6. **AI Feedback**: ML-based pronunciation assessment
7. **Mobile App**: Native mobile application support
8. **Offline Mode**: Complete offline support

## Support & Debugging

### Enable Debug Logging
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Pronunciation Trainer Logs
```
✅ Generated pronunciation for 'word'
🎵 Processing audio: 2.50s @ 16000Hz
✅ Recognized: 'word'
3️⃣ Comparing pronunciation...
📊 RESULT: Similarity: 0.95, Match: True
```

### Check Backend Availability
```bash
curl http://localhost:8000/health
# Returns: {"status": "🟢 Healthy", "model": "Vosk loaded"}
```

## License & Attribution

- **Vosk**: Apache 2.0
- **pyttsx3**: MIT
- **FastAPI**: MIT
- **React**: MIT

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-08  
**Status**: ✅ Production Ready
