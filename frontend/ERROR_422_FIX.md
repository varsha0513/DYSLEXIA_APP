# 🔧 422 Error Fix & Troubleshooting Guide

## The Problem: Error 422 "Unprocessable Entity"

You're getting a 422 error when trying to submit the audio file to the backend.

## ✅ What I Fixed

I've made **4 major improvements** to handle the 422 error:

### 1. **Proper WAV Encoding** ✅
- The audio is now properly encoded as valid WAV files with correct RIFF headers
- Sample rate is automatically resampled to 16000 Hz (what backend expects)
- 16-bit PCM format with proper headers

### 2. **Better Error Messages** ✅
- Detailed console logging at every step
- Clear error messages showing exactly what went wrong
- Network tab shows actual backend response

### 3. **Audio Validation** ✅
- Checks audio blob is not empty
- Validates audio file is at least 1KB
- Ensures audio was captured (not silent)
- Verifies all parameters before sending

### 4. **Audio Resampling** ✅
- Automatically resamples from browser's native sample rate (44100 or 48000 Hz) to 16000 Hz
- Linear interpolation for quality resampling
- Logs the resampling process

## 🚀 How to Test Now

### Step 1: Check Console Logs
1. Open **http://localhost:3000**
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. You should see helpful messages with emojis

Expected flow:
```
🎤 Requesting microphone access...
✅ Microphone accessed
🎵 Audio context created - Sample rate: 48000 Hz
🎙️ Audio capture started - Speak now!
📊 Audio processing: 10 chunks captured
📦 Processing 300000 audio samples...
📊 Resampled audio: 300000 samples @ 48000Hz -> 187500 samples @ 16000Hz
🔧 WavEncoder initialized: 16000Hz, 1 channel(s)
✅ WAV encoding complete: 600.54 KB
📤 Sending assessment request: ...
✅ Assessment completed successfully
```

### Step 2: Run Audio Diagnostic Test
The app now includes a diagnostic script:

1. Open **http://localhost:3000**
2. Open DevTools (**F12**)
3. Copy & paste the entire contents of `test-audio-diagnostic.js`
4. Press Enter
5. Speak when prompted
6. See results

This will test:
- ✅ Web Audio API support
- ✅ Microphone access
- ✅ Audio recording
- ✅ WAV encoding
- ✅ Backend connection

## 🎤 Before You Record

Make sure:
- [ ] Backend is running: `python backend/app.py`
- [ ] Frontend is running: `npm run dev`
- [ ] Microphone is connected and working
- [ ] Browser permissions allow microphone access
- [ ] You'll speak clearly for 5-10 seconds
- [ ] DevTools is open to see logs

## 📋 Common 422 Error Causes & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 error with `[object Object]` | Malformed form data | ✅ Fixed - now uses proper FormData |
| No audio captured | Recording not working | ✅ Fixed - validation & logging added |
| Audio too short | Recording < 1 second | Speak for 5-10 seconds minimum |
| Backend 422 response | Invalid audio format | ✅ Fixed - now sends proper 16kHz WAV |
| "No response from server" | Backend not running | Start: `python backend/app.py` |

## 🔍 Debugging Steps

### If you still get an error:

1. **Check Browser Console** (F12)
   - Look for red errors with ❌
   - Check the last message printed
   
2. **Check Network Tab** (F12 → Network)
   - Click the POST request to `/assess`
   - Look at **Response** tab
   - Screenshot the error for debugging

3. **Check Backend Terminal**
   - Look for error messages
   - Check if audio processing failed

4. **Run Diagnostic**
   - Paste `test-audio-diagnostic.js` in console
   - See what works and what doesn't

## 📝 File Changes Made

### New Files:
- `src/utils/audioEncoder.ts` - Proper WAV encoding
- `src/utils/audioResampler.ts` - Audio resampling to 16000 Hz
- `DEBUG_GUIDE.md` - Detailed debugging guide
- `test-audio-diagnostic.js` - Audio diagnostic script

### Updated Files:
- `src/components/ReadingTask.tsx` - Uses Web Audio API + ScriptProcessor + resampling
- `src/api.ts` - Better error handling and logging
- `src/App.tsx` - Backend health check on startup

## 🎵 Audio Processing Pipeline

```
Browser Recording
     ↓
[Float32Array]  (browser's native sample rate: 44100, 48000, etc.)
     ↓
AudioResampler
     ↓
[Float32Array]  (16000 Hz)
     ↓
WavEncoder
     ↓
WAV ArrayBuffer (with RIFF headers)
     ↓
Blob (audio/wav)
     ↓
FormData with age + paragraph + audio_file
     ↓
POST to http://localhost:8000/assess
     ↓
Backend processes and returns results
```

## ✨ Best Practices Going Forward

1. **Always check console** - logs tell you exactly what's happening
2. **Record for 5-10 seconds** - short audio might be rejected
3. **Speak clearly** - minimize background noise
4. **Test backend first** - make sure it's running and healthy
5. **Use Chrome/Edge** - best browser support

## 📞 Still Having Issues?

1. **Check console logs** - they have all the info
2. **Screenshot the error** - send console error + network response
3. **Try the diagnostic script** - it will pinpoint the issue
4. **Try incognito mode** - avoid cache issues (Ctrl+Shift+N)
5. **Force refresh** - Ctrl+Shift+R

---

**Version**: 2.0 (with WAV encoding, resampling, and better error handling)
**Last Updated**: 2026-02-24
