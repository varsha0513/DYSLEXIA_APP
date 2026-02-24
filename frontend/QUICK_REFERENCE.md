# ⚡ Quick Reference Card

## 🚀 Get Started in 30 Seconds

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend  
cd frontend
npm run dev
```

Open **http://localhost:3000** → Enter age → Read paragraph → See results! 

## 🔗 Key URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Backend Health**: http://localhost:8000/health

## 🎯 The Flow

```
1. Enter Age
   ↓
2. See Paragraph (age-appropriate)
   ↓
3. Click "Start Reading"
   ↓
4. Speak for 5-10 seconds
   ↓
5. Click "Stop & Submit"
   ↓
6. Wait for processing (10-30 sec)
   ↓
7. See Results with:
   ✅ Accuracy %
   🎤 WPM
   ⚠️ Risk Level
   📊 Detailed Feedback
```

## 🐛 Error 422? Do This:

1. **Open Console** (F12)
2. **Look at last log message** with ❌ or 📤
3. **Tell you exactly what's wrong**

Common issues:
- No audio recorded → Record louder
- Audio too short → Record 5-10 seconds
- Backend not running → `python backend/app.py`
- Microphone not working → Check browser permissions

## 📊 Console Messages

| Message | Meaning |
|---------|---------|
| 🎤 Requesting microphone | About to ask for mic permission |
| ✅ Microphone accessed | Mic is ready |
| 🎵 Audio context created | Recording is starting |
| 🎙️ Audio capture started | Now speak! |
| 📦 Processing X samples | Processing audio |
| 📊 Resampled audio | Converting to 16000Hz |
| ✅ WAV encoding complete | Audio ready |
| 📤 Sending assessment request | Uploading to backend |
| ✅ Assessment completed | Results received! |
| ❌ Error message | Something went wrong |

## 🔧 Diagnostic Test

Paste this in console (F12) to test everything:
```javascript
// Copy entire contents of test-audio-diagnostic.js and paste here
```

## 📋 Checklist

Before recording:
- [ ] Backend running
- [ ] Frontend running  
- [ ] Microphone connected
- [ ] Permissions granted
- [ ] No background noise
- [ ] Console open (F12)

## 🎤 Recording Tips

✅ DO:
- Speak clearly and naturally
- Record for 5-10 seconds minimum
- Minimize background noise
- Speak at normal pace

❌ DON'T:
- Record for less than 1 second
- Speak too quietly
- Have loud background noise
- Rush through the text

## 📦 What Gets Sent to Backend

```json
{
  "age": 10,
  "paragraph": "Full text of the paragraph...",
  "audio_file": "WAV audio file (16kHz, 16-bit PCM, mono)"
}
```

Backend returns:
```json
{
  "accuracy_metrics": {
    "accuracy_percent": 85.5,
    "correct_words": 42,
    "wrong_words": 3,
    "missing_words": 2,
    "extra_words": 1
  },
  "speed_metrics": {
    "wpm": 125,
    "speed_category": "Normal",
    "dyslexia_risk": "Low"
  },
  "risk_assessment": {
    "risk_level": "LOW",
    "risk_score": 15.5
    // ... more details
  }
}
```

## 🌐 Browser Support

✅ **Works:**
- Chrome/Chromium (best)
- Edge
- Safari
- Opera

❌ **Problematic:**
- Firefox (Web Audio limitations)
- Very old browsers

## 📁 Important Files

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Main app logic |
| `frontend/src/components/ReadingTask.tsx` | Recording interface |
| `frontend/src/api.ts` | Backend communication |
| `frontend/src/utils/audioEncoder.ts` | WAV encoding |
| `frontend/src/utils/audioResampler.ts` | Audio resampling |
| `backend/app.py` | FastAPI backend |

## 🆘 Emergency Debugging

Not sure what's wrong?

1. **Check backend is running**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "🟢 Healthy", "model": "Vosk loaded"}
   ```

2. **Check frontend is running**
   - Visit http://localhost:3000
   - Should load the age input page

3. **Check browser console**
   - F12 → Console
   - Look for errors starting with ❌

4. **Check network tab**
   - F12 → Network
   - Record and submit
   - Click POST request to `/assess`
   - Check Response tab for error details

5. **Run diagnostic**
   - Copy test-audio-diagnostic.js to console
   - It will tell you what's broken

## 💡 Pro Tips

- **Incognito mode** avoids cache issues
- **Hard refresh** (Ctrl+Shift+R) clears cache
- **Different browser** if one doesn't work
- **Restart both** frontend and backend if having issues

---

**Questions?** Check `DEBUG_GUIDE.md` or `ERROR_422_FIX.md` for detailed info.
