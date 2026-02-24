# 🧠 Dyslexia Assessment Frontend

A modern React + TypeScript frontend for the dyslexia assessment app.

## Features

✅ **Age-Based Assessment** - Customized paragraph difficulty based on age  
🎤 **Live Speech Recognition** - Real-time recognition feedback as users read  
📊 **Comprehensive Results** - Accuracy %, WPM, Risk Level with detailed feedback  
📱 **Responsive Design** - Works on desktop and mobile devices  
🎨 **Beautiful UI** - Modern, accessible interface with smooth animations  

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AgeInput.tsx          # Age input form
│   │   ├── ReadingTask.tsx       # Reading interface with recording
│   │   ├── ResultsDisplay.tsx    # Results visualization
│   │   ├── Loading.tsx           # Loading spinner
│   │   └── ErrorDisplay.tsx      # Error handling
│   ├── hooks/
│   │   └── useMediaRecorder.ts   # Media recording hook
│   ├── paragraphs.ts            # Age-based paragraphs
│   ├── api.ts                   # Backend API calls
│   ├── types.ts                 # TypeScript interfaces
│   ├── App.tsx                  # Main app component
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── package.json                # Dependencies
└── index.html                  # HTML template
```

## Installation

1. Navigate to the frontend directory:
```bash
cd c:\Users\varsh\DYSLEXIA_APP\frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Frontend

### Development Mode
```bash
npm run dev
```

Opens at `http://localhost:3000`

### Production Build
```bash
npm run build
npm run preview
```

## How It Works

### 1. **Age Input**
   - User enters their age (5-100)
   - Age determines paragraph difficulty

### 2. **Reading Assessment**
   - Displays age-appropriate paragraph
   - Records user reading via microphone
   - Shows live speech recognition
   - Sends audio to backend for processing

### 3. **Results**
   - **Accuracy %** - Word-by-word accuracy
   - **WPM** - Words per minute reading speed
   - **Risk Level** - Dyslexia risk assessment
   - **Detailed Feedback** - Performance breakdown, recommendations

## Backend Integration

The frontend communicates with the backend API at `http://localhost:8000`:

```
POST /assess
├── age: number
├── paragraph: string
└── audio_file: WAV file
      ↓
Returns AssessmentResponse with:
├── accuracy_metrics
├── speed_metrics
├── risk_assessment
└── feedback
```

## Environment Setup

Make sure the backend is running:
```bash
cd c:\Users\varsh\DYSLEXIA_APP\backend
python app.py
```

The backend should be running on `http://localhost:8000`

## Browser Requirements

- Modern browser with Web Speech API support (Chrome, Edge, Safari)
- Microphone access permissions
- CORS enabled (backend already has CORS middleware)

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **Web Speech API** - Live speech recognition
- **MediaRecorder API** - Audio recording

## Troubleshooting

### Microphone Not Working
- Check browser permissions for microphone
- Ensure microphone is connected and working
- Try a different browser

### Backend Connection Error
- Verify backend is running: `http://localhost:8000`
- Check CORS settings in backend
- Ensure both frontend and backend are on correct ports

### Audio Not Processing
- Make sure audio is recorded in WAV format
- Check audio is 16-bit, 16kHz, mono
- Verify backend model is loaded correctly

## Development Tips

- Use React DevTools for debugging components
- Check browser console for API errors
- Monitor network tab in DevTools for API requests
- Test with different age groups for variety in paragraphs

---

Created for the Dyslexia Assessment System
