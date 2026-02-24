# 🐛 Frontend Debugging Guide

## Issue: Error 422 "Unprocessable Entity"

This error means the backend cannot process the data you sent. Here are the common causes and solutions:

### ✅ How to Debug

1. **Open Browser Console**
   - Press `F12` or `Ctrl+Shift+I`
   - Go to **Console** tab
   - Look for messages starting with 📤, 📊, ✅, or ❌

2. **Check the Logs**
   ```
   🎤 Requesting microphone access...
   ✅ Microphone accessed
   🎵 Audio context created - Sample rate: 48000 Hz
   🎙️ Audio capture started - Speak now!
   📊 Audio processing: 10 chunks captured
   📦 Processing 300000 audio samples...
   📊 Resampled audio: 300000 samples @ 48000Hz -> 187500 samples @ 16000Hz
   🔧 WavEncoder initialized: 16000Hz, 1 channel(s)
   📦 Encoding 187500 samples...
   ✅ WAV encoding complete: 600.54 KB
   ✅ WAV file created: 600.54 KB
   📤 Sending assessment request...
   ```

### ❌ Common Issues & Solutions

#### Issue 1: "No audio recorded"
**Symptoms:**
- Error: "No audio was captured"
- Console: Shows 0 chunks captured

**Solutions:**
- [ ] Check microphone is plugged in and working
- [ ] Allow microphone permission when browser asks
- [ ] Try a different browser (Chrome/Edge recommended)
- [ ] Test microphone in system settings first
- [ ] Close other apps using microphone

#### Issue 2: "Audio file is too small"
**Symptoms:**
- Error: "Audio file is too small"
- File size < 1 KB

**Solutions:**
- [ ] Record for at least 5-10 seconds
- [ ] Speak loudly and clearly
- [ ] Reduce background noise
- [ ] Move closer to microphone

#### Issue 3: Backend returning 422
**Symptoms:**
- Console: "Server error: [object Object]"
- Status 422 when submitting

**Solutions:**
- [ ] Make sure backend is running: `python backend/app.py`
- [ ] Backend should print: "Application startup complete"
- [ ] Check backend is on http://localhost:8000
- [ ] Check network tab (F12 → Network) - look at request/response
- [ ] Make sure audio file size is > 1000 bytes
- [ ] Ensure paragraph is not empty

#### Issue 4: "Backend server not responding"
**Symptoms:**
- Error: "Backend server is not responding"
- Cannot connect to http://localhost:8000

**Solutions:**
- [ ] Start backend in terminal: `cd backend && python app.py`
- [ ] Should print: `INFO:     Uvicorn running on http://127.0.0.1:8000`
- [ ] Check firewall isn't blocking port 8000
- [ ] Check no other app is using port 8000

### 🔍 Network Debugging

To see exact error from backend:

1. Open DevTools (F12)
2. Go to **Network** tab
3. Record audio and submit
4. Look for request to `http://localhost:8000/assess`
5. Click on it
6. Go to **Response** tab
7. See what backend says

Example error response:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "audio_file"],
      "msg": "Invalid audio format",
      "input": "..."
    }
  ]
}
```

### 📋 Checklist Before Recording

- [ ] Microphone connected and working
- [ ] No other apps using microphone
- [ ] Background noise is minimal
- [ ] Backend running (`python backend/app.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] Browser is Chrome, Edge, or Safari
- [ ] DevTools open to see console logs

### 🎙️ Audio Requirements

Backend expects audio with these specifications:
- **Format**: WAV (RIFF)
- **Encoding**: 16-bit PCM
- **Sample Rate**: 16000 Hz (will be resampled automatically)
- **Channels**: 1 (mono)
- **Minimum Duration**: 1-2 seconds
- **Minimum File Size**: 1000 bytes (~0.5 KB)

### 📊 What's Happening Behind the Scenes

1. **Recording (handleStartReading)**
   - Requests microphone access
   - Creates AudioContext at browser's native sample rate (usually 44100 or 48000 Hz)
   - Uses ScriptProcessorNode to capture raw PCM frames

2. **Processing (handleStopReading)**
   - Concatenates all audio frames into one Float32Array
   - Resamples from browser's sample rate to 16000 Hz
   - Encodes to WAV format with proper headers
   - Creates Blob

3. **Sending (assessReading)**
   - Creates FormData with age, paragraph, audio file
   - POSTs to http://localhost:8000/assess
   - Backend processes and returns results

### 💡 Pro Tips

1. **Use Incognito Mode** to avoid cache issues
   - Press `Ctrl+Shift+N`

2. **Force Refresh**
   - Press `Ctrl+Shift+R` (hard refresh)

3. **Check Browser Compatibility**
   ```javascript
   // Paste in console to check
   console.log({
     webAudio: !!window.AudioContext,
     mediaRecorder: !!window.MediaRecorder,
     getUserMedia: !!navigator.mediaDevices?.getUserMedia,
     sampleRate: (new (window.AudioContext || window.webkitAudioContext)()).sampleRate
   })
   ```

4. **Test Microphone First**
   ```javascript
   // Paste in console to test microphone
   navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
     console.log('✅ Microphone works!');
     stream.getTracks().forEach(t => t.stop());
   }).catch(e => console.error('❌ Microphone error:', e));
   ```

### 📞 Still Having Issues?

1. Check console logs with formatting emojis (📤, 📊, ✅, ❌)
2. Check Network tab response
3. Make sure backend is running and returning `/health` status ✅
4. Try recording without background noise
5. Try different browser
6. Restart both frontend and backend

---

**Debug Status:** Open console (F12) and look for logs - they will tell you exactly what's happening! 🔍
