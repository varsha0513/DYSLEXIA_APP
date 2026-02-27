# 🏗️ ASSISTANCE MODULE - SYSTEM ARCHITECTURE

## Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          STUDENT / USER                              │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/TypeScript)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐      ┌──────────────────┐                   │
│  │   AgeInput.tsx   │      │  ReadingTask.tsx │                   │
│  │                  │  →   │  (Records audio) │                   │
│  └──────────────────┘      └──────────────────┘                   │
│                                    ↓                                 │
│                        ┌────────────────────┐                       │
│                        │  Results Display   │                       │
│                        │   .tsx / .css      │                       │
│                        └────────────────────┘                       │
│                                    ↓                                 │
│                    ┌───────────────────────────┐                    │
│                    │  AssistanceWidget.tsx ✨  │                    │
│                    │  (Shows errors + audio)   │                    │
│                    └───────────────────────────┘                    │
│                                    ↓                                 │
│                    [🔊 Hear] [🔄 Repeat] buttons                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                         HTTP REST API calls
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI / Python)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐                                                   │
│  │   app.py     │  (Main API Router)                               │
│  └──────────────┘                                                   │
│         ↓                                                             │
│  ┌──────────────────────────────────────────────┐                   │
│  │  POST /assess                                │                   │
│  │  - Receives audio file                       │                   │
│  │  - Sends to Vosk recognizer                 │                   │
│  │  - Calls compare_text()                      │                   │
│  │  - Gets speed metrics                        │                   │
│  │  - Calculates risk score                     │                   │
│  │  → Returns assessment WITH assistance data  │                   │
│  └──────────────────────────────────────────────┘                   │
│         ↓                                                             │
│  ┌────────────────────────────────────────────────────────┐         │
│  │          text_comparison.py (ENHANCED)                 │         │
│  ├────────────────────────────────────────────────────────┤         │
│  │ compare_text():                                        │         │
│  │   Input: reference_text, spoken_text                  │         │
│  │   Output:                                              │         │
│  │   - total_words, correct, wrong, missing, extra       │         │
│  │   - accuracy_percent                                  │         │
│  │   → word_level_errors (NEW!)                          │         │
│  │                                                        │         │
│  │ get_word_level_errors():                              │         │
│  │   Returns detailed error info:                        │         │
│  │   - wrong_words: [(spoken, correct), ...]            │         │
│  │   - missing_words: [word1, word2, ...]               │         │
│  │   - extra_words: [word1, word2, ...]                 │         │
│  └────────────────────────────────────────────────────────┘         │
│         ↓                                                             │
│  ┌────────────────────────────────────────────────────────┐         │
│  │       text_to_speech.py (NEW MODULE) ✨              │         │
│  ├────────────────────────────────────────────────────────┤         │
│  │ DyslexiaAssistanceEngine:                              │         │
│  │   - Initializes pyttsx3 TTS engine                    │         │
│  │   - generate_audio_file(word)                         │         │
│  │     → Generates WAV audio (88KB)                      │         │
│  │     → Returns (bytes, base64)                         │         │
│  │   - generate_word_assistance(wrong, correct)          │         │
│  │     → Audio + feedback message                        │         │
│  │   - generate_missing_word_assistance(word)            │         │
│  │     → Audio for skipped words                         │         │
│  └────────────────────────────────────────────────────────┘         │
│         ↓                                                             │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ Build AssistanceData object:                           │         │
│  │   {                                                    │         │
│  │     has_errors: bool,                                │         │
│  │     error_count: int,                                │         │
│  │     wrong_words: [[spoken, correct], ...],           │         │
│  │     missing_words: [word, ...],                      │         │
│  │     extra_words: [word, ...],                        │         │
│  │     assistance_enabled: bool                         │         │
│  │   }                                                    │         │
│  └────────────────────────────────────────────────────────┘         │
│         ↓                                                             │
│  ┌──────────────────────────────────────────────────────┐           │
│  │  POST /tts/word                                      │           │
│  │  - Receives word                                     │           │
│  │  - Generates audio via pyttsx3                       │           │
│  │  → Returns WAV file (audio/wav)                      │           │
│  └──────────────────────────────────────────────────────┘           │
│         ↓                                                             │
│  ┌──────────────────────────────────────────────────────┐           │
│  │  POST /tts/correction                                │           │
│  │  - Receives (wrong_word, correct_word)               │           │
│  │  - Generates audio for correct word                  │           │
│  │  - Returns JSON with audio_base64                    │           │
│  │  → Frontend uses data:audio/wav;base64,... URL      │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
│  ┌──────────────────────────┐  ┌──────────────────────────┐        │
│  │  reading_speed.py        │  │  dyslexia_risk_scoring.py│        │
│  │  (SpeedMetrics)          │  │  (RiskAssessment)        │        │
│  └──────────────────────────┘  └──────────────────────────┘        │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │ External: vosk/KaldiRecognizer (Speech Recognition) │           │
│  │ External: pyttsx3 (OpenAI replacement for TTS)      │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                         HTTP Response
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    AssessmentResponse JSON                           │
├─────────────────────────────────────────────────────────────────────┤
│ {                                                                    │
│   "reference_text": "The quick brown fox...",                       │
│   "recognized_text": "The brown fox...",                            │
│   "age": 10,                                                        │
│   "speed_metrics": { wpm, elapsed_time, ... },                     │
│   "accuracy_metrics": { correct: 8, wrong: 1, ... },               │
│   "risk_assessment": { risk_level, risk_score, ... },              │
│   "accuracy_feedback": "Good job!...",                              │
│   "difficulty_assessment": "Current level is appropriate",         │
│                                                                      │
│   "assistance": { ✨ NEW FIELD                                      │
│     "has_errors": true,                                            │
│     "error_count": 1,                                              │
│     "wrong_words": [["brown", "quick"]],                          │
│     "missing_words": [],                                           │
│     "extra_words": [],                                             │
│     "assistance_enabled": true                                     │
│   },                                                                │
│                                                                      │
│   "status": "success"                                               │
│ }                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
         Frontend displays results with AssistanceWidget
                              ↓
                    User clicks [🔊 Hear]
                              ↓
                   fetch POST /tts/word
                              ↓
               Backend generates audio file
                              ↓
                   HTML <audio> plays it
                              ↓
                Student hears pronunciation
```

---

## Data Flow Diagram

```
STEP 1: Assessment Collection
┌─────────────────┐
│ Student Reads   │
│ Paragraph       │
└────────┬────────┘
         ↓
   Browser Records
   Audio Blob
         ↓
┌──────────────────────────────────┐
│ Send to /assess with:            │
│ - age: number                    │
│ - paragraph: string              │
│ - audio_file: Blob               │
│ - recognized_text?: string       │
└──────────────────────────────────┘

STEP 2: Speech Recognition
┌──────────────────────────────────┐
│ Vosk Speech Recognizer           │
│ Processes audio stream           │
│ Extracts text from speech        │
└──────────────────────────────────┘

STEP 3: Text Comparison
┌──────────────────────────────────┐
│ compare_text()                   │
│ Reference vs. Spoken             │
│ Returns:                         │
│ - Accuracy metrics               │
│ - Word-level errors              │
└──────────────────────────────────┘

STEP 4: Assistance Generation
┌──────────────────────────────────┐
│ TTS Engine processes errors:     │
│ For each wrong word:             │
│  1. Generate audio               │
│  2. Encode to base64             │
│  3. Create feedback message      │
└──────────────────────────────────┘

STEP 5: Response Assembly
┌──────────────────────────────────┐
│ Build AssessmentResponse:        │
│ - Include metrics                │
│ - Include risk assessment        │
│ - Include ASSISTANCE DATA ✨     │
└──────────────────────────────────┘

STEP 6: Frontend Display
┌──────────────────────────────────┐
│ Show Results                     │
│ + AssistanceWidget with:         │
│ - [🔊 Hear] buttons              │
│ - Word comparisons               │
│ - Practice instructions          │
└──────────────────────────────────┘

STEP 7: Student Practice
┌──────────────────────────────────┐
│ Student clicks [🔊 Hear]         │
│ Frontend fetches /tts/word       │
│ Audio plays                      │
│ Student practices                │
│ Student can reassess             │
└──────────────────────────────────┘
```

---

## Component Relationships

```
App.tsx (Main)
├── AgeInput.tsx
│   └── Collects age
│
├── ReadingTask.tsx
│   ├── Displays paragraph
│   ├── Records audio
│   └── useMediaRecorder hook
│
├── ResultsDisplay.tsx
│   ├── Shows metrics
│   ├── Shows analysis
│   ├── Shows risk assessment
│   └── AssistanceWidget ✨ (NEW)
│       ├── Shows word errors
│       ├── Shows missing words
│       ├── Play button → fetch /tts/word
│       └── Repeat button → repeat audio
│
└── ErrorDisplay.tsx
    └── Shows errors if any
```

---

## File Organization

```
DYSLEXIA_APP/
├── backend/
│   ├── app.py (UPDATED)
│   │   - Added TTS imports
│   │   - Added TTS initialization
│   │   - Added /tts/word endpoint
│   │   - Added /tts/correction endpoint
│   │   - Added AssistanceData model
│   │
│   ├── text_comparison.py (UPDATED)
│   │   - Added get_word_level_errors()
│   │   - Enhanced compare_text()
│   │
│   ├── text_to_speech.py (NEW) ✨
│   │   - DyslexiaAssistanceEngine class
│   │   - TTS methods for words
│   │
│   ├── reading_speed.py
│   ├── dyslexia_risk_scoring.py
│   └── complete_reading_assessment.py
│
├── frontend/
│   ├── src/
│   │   ├── types.ts (UPDATED)
│   │   │   - Added AssistanceData interface
│   │   │
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   │
│   │   └── components/
│   │       ├── AgeInput.tsx
│   │       ├── ReadingTask.tsx
│   │       ├── ResultsDisplay.tsx (UPDATED)
│   │       │   - Imports AssistanceWidget
│   │       │   - Renders it conditionally
│   │       │
│   │       ├── AssistanceWidget.tsx (NEW) ✨
│   │       │   - Shows errors
│   │       │   - Audio controls
│   │       │   - Practice guide
│   │       │
│   │       ├── AssistanceWidget.css (NEW) ✨
│   │       │   - Styling
│   │       │   - Responsive design
│   │       │
│   │       ├── ErrorDisplay.tsx
│   │       └── Loading.tsx
│   │
│   └── [other config files]
│
├── requirements.txt (UPDATED)
│   - Added pyttsx3>=2.90
│
└── Documentation
    ├── README_ASSISTANCE_MODULE.md (NEW) ✨
    ├── ASSISTANCE_MODULE_GUIDE.md (NEW) ✨
    ├── ASSISTANCE_QUICK_START.md (NEW) ✨
    ├── API_REFERENCE_ASSISTANCE.md (NEW) ✨
    ├── ASSISTANCE_MODULE_VERIFICATION.md (NEW) ✨
    ├── SYSTEM_ARCHITECTURE.md (Updated to include this)
    └── [other docs]
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│              TECHNOLOGY STACK                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  FRONTEND                                       │
│  - React 18+                                   │
│  - TypeScript                                   │
│  - CSS3 (Gradient, Glass-morphism)             │
│  - HTML5 Audio API                             │
│  - Axios (HTTP client)                         │
│                                                 │
│  BACKEND                                        │
│  - Python 3.7+                                 │
│  - FastAPI (REST API framework)                │
│  - Pydantic (Data validation)                  │
│  - pyttsx3 (Text-to-Speech)                   │
│  - Vosk (Speech Recognition)                  │
│  - uvicorn (ASGI server)                       │
│                                                 │
│  EXTERNAL LIBRARIES                             │
│  - NumPy (Audio processing)                    │
│  - sounddevice (Audio I/O)                     │
│  - python-multipart (Form handling)            │
│                                                 │
│  DEPLOYMENT                                     │
│  - Docker-ready (optional)                    │
│  - Cross-platform (Windows/Mac/Linux)         │
│  - Offline-capable                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## State Management Flow

```
Student Assessment
        ↓
Create Assessment State
        ↓
┌─────────────────────────────┐
│ appState: 'age-input'       │
│ age: number                 │
│ paragraph: string           │
│ audioBlob: Blob             │
│ recognizedText: string      │
│ results: AssessmentResponse │
│ error: string               │
└─────────────────────────────┘
        ↓
State Transitions
  'age-input' → 'reading' (age selected)
  'reading' → 'loading' (audio submitted)
  'loading' → 'results' (assessment complete)
  'loading' → 'error' (if assessment fails)
  'results' → 'age-input' (restart)
        ↓
Results include AssistanceData ✨
        ↓
AssistanceWidget receives assistance
        ↓
Component displays errors & controls
```

---

## Error Handling Strategy

```
FRONTEND ERRORS
├── Audio Recording Failed
│   → Show error message
│   → Suggest microphone check
│   → Allow retry
│
├── API Request Failed
│   → Show HTTP error
│   → Show retry button
│   → Log to console
│
├── Audio Playback Failed
│   → Disable play button
│   → Show error message
│   → Continue normally
│
└── Missing Assistance Data
    → Widget doesn't render
    → Results still show
    → System continues normally

BACKEND ERRORS
├── TTS Engine Not Available
│   → Log warning
│   → Continue without assistance
│   → Set assistance_enabled: false
│
├── Audio Generation Failed
│   → Log error
│   → Return error status
│   → Frontend shows "TTS unavailable"
│
└── Vosk Recognition Failed
    → Continue with empty recognition
    → Show "No speech detected"
    → Allow retry
```

---

## Performance Optimization

```
AUDIO CACHING (Frontend)
- Cache audio blobs by word
- Reuse for repeat plays
- Clear cache on page unload

LAZY LOADING
- Load components only when needed
- AssistanceWidget only if errors

BATCH PROCESSING
- Generate all word audios together
- Return in single response

API OPTIMIZATION
- Compress base64 audio
- Use streaming for large files
- Keep responses under 1MB

FRONTEND OPTIMIZATION
- Use refs for audio elements
- Prevent re-renders with useMemo
- React.memo for static components
```

---

## Security Considerations

```
INPUT VALIDATION
├── Word length 1-100 chars
├── No special characters except spaces
├── Type checking in TypeScript
└── Server-side validation

AUDIO SECURITY
├── No audio stored on server
├── Generated on-demand
├── Deleted after transmission
└── No history kept

API SECURITY
├── CORS enabled (can restrict)
├── No authentication needed (public tool)
├── Rate limiting (optional)
└── Input sanitization

FRONTEND SECURITY
├── React XSS protection built-in
├── No eval() or dangerous functions
├── Safe HTML rendering
└── Type-safe with TypeScript
```

---

## Scalability Notes

```
HORIZONTAL SCALING
- Stateless API (can run multiple instances)
- No server-side audio storage
- Each instance independent

PERFORMANCE LIMITS
- ~50-100ms per audio generation (pyttsx3)
- ~500KB RAM per concurrent request
- ~100 concurrent users on modern hardware

OPTIMIZATION OPPORTUNITIES
- Use audio caching layer
- Pre-generate common words
- Use CDN for audio delivery
- Cloud TTS service (if scaling beyond local)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 27, 2026 | Initial release with Assistance Module |
| 0.9 | Feb 20, 2026 | Core assessment system |
| 0.8 | Feb 10, 2026 | Speech recognition |
| 0.7 | Feb 1, 2026 | Risk scoring |

---

## Future Architecture Additions

```
Phase 2: Word Practice Mode
┌─────────────────────────────┐
│ PracticeMode Component      │
│ - Record 3x repetitions     │
│ - Measure confidence        │
│ - Score pronunciation       │
│ → POST /tts/evaluate (new) │
└─────────────────────────────┘

Phase 3: Analytics
┌─────────────────────────────┐
│ AnalyticsDashboard          │
│ - Track word difficulty     │
│ - Show progress             │
│ - Recommend practice        │
│ → POST /analytics (new)    │
└─────────────────────────────┘

Phase 4: Social Learning
┌─────────────────────────────┐
│ SharedLearning Component    │
│ - Share results with teacher│
│ - Compare with peers        │
│ - Leaderboards              │
│ → New database schema      │
└─────────────────────────────┘
```

---

**Architecture Version**: 1.0 - Assistance Module
**Last Updated**: February 27, 2026
**Status**: Production Ready ✅
