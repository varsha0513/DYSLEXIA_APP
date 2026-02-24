# 🚀 Frontend Quick Start Guide

## Prerequisites
- Node.js 16+ installed
- Backend running on `http://localhost:8000`
- Microphone connected

## Quick Setup (5 minutes)

### 1️⃣ Install Dependencies
```powershell
cd c:\Users\varsh\DYSLEXIA_APP\frontend
npm install
```

### 2️⃣ Start Development Server
```powershell
npm run dev
```

### 3️⃣ Open in Browser
Navigate to: **http://localhost:3000**

## What Happens Next

### Step 1: Age Input (Age Selection)
- Enter your age
- Click "Start Assessment"

### Step 2: Reading Task (Recording)
- Read the paragraph clearly
- Click "Start Reading" to begin recording
- Speak naturally at your pace
- Click "Stop & Submit" when done
- **Live recognition will display** as you speak

### Step 3: Results (Assessment Complete)
Display shows:
```
┌─────────────────────────────────┐
│  85.5% Accuracy                 │
│  125 WPM                         │
│  LOW Risk                        │
└─────────────────────────────────┘
```

Plus detailed breakdown:
- ✓ Correct words
- ⚠ Wrong words  
- ✗ Missing words
- + Extra words
- 📊 Risk assessment with recommendations

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Failed to access microphone" | Browser needs permission, check browser settings |
| "Backend not responding" | Start backend: `python backend/app.py` |
| "No speech detected" | Speak louder closer to microphone |
| "Empty results" | Check browser console for errors |

## File Structure for Reference

```
frontend/
├── src/
│   ├── App.tsx                  ← Main state management
│   ├── components/
│   │   ├── AgeInput.tsx        ← Step 1
│   │   ├── ReadingTask.tsx     ← Step 2 (with recording)
│   │   ├── ResultsDisplay.tsx  ← Step 3
│   │   ├── Loading.tsx
│   │   └── ErrorDisplay.tsx
│   ├── paragraphs.ts           ← Age-appropriate texts
│   ├── api.ts                  ← Backend integration
│   └── hooks/useMediaRecorder.ts ← Audio handling
└── package.json                ← Dependencies
```

## Key Features Implemented ✅

- [x] Age input form (5-100 years)
- [x] Display paragraph based on age
- [x] Microphone recording with MediaRecorder API
- [x] Live speech recognition (Web Speech API)
- [x] POST to `/assess` endpoint
- [x] Accuracy % display
- [x] WPM calculation
- [x] Risk Level visualization
- [x] Detailed feedback section
- [x] Word-by-word breakdown
- [x] Risk assessment details
- [x] Recommendations list
- [x] Beautiful responsive UI
- [x] Error handling

## Build for Production

```powershell
npm run build
```

Creates optimized `dist/` folder for deployment

---

**Ready to go!** 🚀
