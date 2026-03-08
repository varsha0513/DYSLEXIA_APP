# Pronunciation Module - Quick Reference Card

## 🚀 Quick Start (2 minutes)

```bash
# 1. Start Backend
cd backend
python app.py
# Expected: "✅ Pronunciation Trainer ready"

# 2. Start Frontend  
cd frontend
npm run dev
# Expected: "➜ Local: http://localhost:5173/"

# 3. Test Everything
python backend/test_pronunciation.py
# Expected: "🎉 All tests passed! Success Rate: 100%"
```

## 📁 Key Files at a Glance

| File | Purpose | Key Functions |
|------|---------|---|
| `pronunciation_trainer.py` | Core trainer | `speak_word()`, `listen_word()`, `check_pronunciation()` |
| `PronunciationTrainingWidget.tsx` | Frontend UI | Recording, playback, feedback display |
| `test_pronunciation.py` | Testing | Auto-verify all systems |

## 🔗 API Endpoints

| Method | Endpoint | Input | Output |
|--------|----------|-------|--------|
| **POST** | `/pronunciation/word-audio` | `word` | Audio (WAV) |
| **POST** | `/pronunciation/check` | `word`, `audio_file` | Feedback JSON |
| **POST** | `/pronunciation/word-comparison` | `spoken_word`, `target_word` | Similarity metrics |
| **POST** | `/pronunciation/batch-check` | `words` (JSON) | Ready status |

## 🎯 How It Works

```
User clicks "Hear It"
        ↓
speak_word() → TTS generates audio
        ↓
User records word
        ↓
listen_word() → Vosk converts to text
        ↓
check_pronunciation() → Compare with target
        ↓
Return feedback with similarity score
        ↓
User sees: "95% similar - Great job!"
```

## ⚙️ Configuration

```python
# TTS Speed (default: 100 = normal)
tts_engine = DyslexiaAssistanceEngine(rate=80)  # Slower/faster

# Similarity Threshold (default: 0.85 = 85%)
is_correct = similarity_ratio > 0.85  # Stricter or lenient

# Max Attempts (default: 3)
if state.attempts >= 3: /* show skip button */
```

## 🧪 Testing

```bash
# Full test suite
python backend/test_pronunciation.py

# Quick manual test
curl -X POST http://localhost:8000/pronunciation/word-audio \
  -F "word=pronunciation" -o test.wav

# Check word comparison
curl -X POST http://localhost:8000/pronunciation/word-comparison \
  -F "spoken_word=pronuncation" -F "target_word=pronunciation"
```

## 🐛 Common Errors

| Problem | Solution |
|---------|----------|
| Backend 503 TTS not available | `pip install --upgrade pyttsx3` |
| Vosk model not found | Download to `model/vosk-model-small-en-us-0.15/` |
| Microphone denied | Grant browser permission (address bar lock icon) |
| No speech recognized | Ensure clear audio, lower background noise |
| Audio playback fails | Check system volume, try different browser |

## 📊 Performance Targets

- **TTS Generation**: 1-2 seconds
- **Speech Recognition**: 0.5-1.5 seconds
- **Word Comparison**: <10ms
- **Total per Attempt**: 2-4 seconds

## 🎨 UI Components

```typescript
// Main component
<PronunciationTrainingWidget
  words={["pronunciation", "assistant"]}
  onComplete={(results) => console.log(results)}
/>

// Props
words: string[]                           // Words to practice
onComplete?: (results: TrainingResult[]) => void  // Callback
```

## 🔌 Integration Points

```typescript
// In ResultsDisplay.tsx
<PronunciationTrainingWidget
  words={[
    ...results.assistance.wrong_words.map(([_, correct]) => correct),
    ...results.assistance.missing_words,
  ]}
/>
```

## Similarity Score Meanings

- **100%**: Exact match
- **85-99%**: Accept as correct (minor variation)
- **70-84%**: Close attempt, retry encouraged
- **<70%**: Significant difference, retry recommended

## Browser Requirements

✅ Chrome/Edge (latest)  
✅ Firefox (latest)  
✅ Safari (latest)  
⚠️ HTTPS recommended for microphone access

## Dependencies

**Backend**: `pyttsx3`, `vosk`, `fastapi`  
**Frontend**: `React`, `TypeScript`, Web Audio API  
**System**: Python 3.7+, Vosk model

## Key Features

🔊 Text-to-speech for correct pronunciation  
🎤 Microphone recording & audio capture  
🧠 Vosk speech recognition engine  
📊 Similarity-based comparison (0-100%)  
🔄 Retry mechanism with attempt counter  
✨ Real-time feedback with progress tracking  
📱 Responsive design for mobile

## Troubleshooting Checklist

- [ ] Backend running? (`python app.py`)
- [ ] Frontend running? (`npm run dev`)
- [ ] Vosk model downloaded? (`model/` folder)
- [ ] Microphone permission granted?
- [ ] Audio speaker working? (Test with "Hear It")
- [ ] No console errors? (Open DevTools F12)
- [ ] Backend logs show no errors?

## Important Phone Numbers (For REST API)

```
GET  /health                          → Status check
POST /pronunciation/word-audio        → Generate audio
POST /pronunciation/check             → Check pronunciation
POST /pronunciation/word-comparison   → Compare words
POST /pronunciation/batch-check       → Batch operation
```

## Next Steps After Setup

1. Run test suite: `python backend/test_pronunciation.py`
2. Take an assessment to trigger pronunciation training
3. Review logs: Check both terminal windows
4. Customize: Adjust TTS speed/similarity threshold as needed
5. Deploy: Follow deployment guide in main docs

## Documentation Links

📖 **Full Guide**: `PRONUNCIATION_MODULE_GUIDE.md`  
⚡ **Quick Start**: `PRONUNCIATION_QUICK_START.md`  
✅ **Checklist**: `PRONUNCIATION_IMPLEMENTATION_CHECKLIST.md`  
📋 **Summary**: `PRONUNCIATION_IMPLEMENTATION_SUMMARY.md`

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open DevTools | F12 |
| Reload page | Ctrl+R / Cmd+R |
| View logs | Browser console or Terminal |
| Stop server | Ctrl+C |

## Support Resources

```python
# Check backend status
curl http://localhost:8000/health

# View app info
curl http://localhost:8000/

# Debug logs enabled by default
# Check terminal or browser console
```

## One-Line Commands

```bash
# Start everything
# Terminal 1:
cd backend && python app.py

# Terminal 2:
cd frontend && npm run dev

# Terminal 3:
python backend/test_pronunciation.py
```

## Model Architecture

```
Input (word + audio)
    ↓
[Vosk] → Speech-to-text
    ↓
Normalize words
    ↓
[difflib] → Calculate similarity
    ↓
Decision logic (exact match OR similarity > 0.85)
    ↓
Output (feedback + audio + metrics)
```

## Metrics Explained

```json
{
  "similarity_ratio": 0.92,      // 0-1 scale, higher = similar
  "is_exact_match": false,       // Word-for-word identical
  "is_correct": true,            // Exact OR similarity > 0.85
  "feedback": "Great job!",      // User-friendly message
  "pronunciation_audio": "base64" // Audio to replay
}
```

## Version Info

**Module Version**: 1.0.0  
**Release Date**: 2026-03-08  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-03-08

---

**Need help?** Check the full documentation in `PRONUNCIATION_MODULE_GUIDE.md`

**Quick test?** Run `python backend/test_pronunciation.py`

**Ready to go?** You're all set! 🚀
