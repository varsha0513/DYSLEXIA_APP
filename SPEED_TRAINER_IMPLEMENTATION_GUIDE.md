# Guided Pace Reading (Speed Trainer) - Implementation Guide

## Overview

The Speed Trainer feature is a comprehensive guided pace reading system designed to help users improve their reading speed through progressive training. The system uses word-by-word highlighting with increasing WPM (Words Per Minute) across three training rounds, from 60 WPM to 90 WPM.

## Features Implemented

### ✅ Backend Features (FastAPI)

1. **Session Management**
   - Create and manage speed training sessions
   - Store session state and progress
   - Track multiple rounds with different speeds

2. **Text Processing**
   - Split paragraphs into individual words
   - Clean punctuation while preserving word integrity
   - Support for various text formats

3. **Speed Calculation**
   - Calculate word highlighting intervals: `interval_ms = 60000 / WPM`
   - Three training rounds: 60 WPM → 75 WPM → 90 WPM
   - Calculate round duration based on word count and WPM

4. **Result Tracking**
   - Track actual reading time
   - Calculate real WPM from elapsed time
   - Store session statistics

### ✅ Frontend Features (React + TypeScript)

1. **Interactive Training Interface**
   - Word-by-word text display with highlighting
   - Real-time progress tracking with visual progress bar
   - Current word emphasis display for better focus

2. **Training Controls**
   - Start/Resume button for initiating training
   - Pause button to pause during training
   - Reset button to restart the session
   - Countdown overlay (3, 2, 1, Go!) before each session

3. **Visual Feedback**
   - Highlighted words with smooth animations
   - Current word displayed in large font
   - Progress bar showing completion percentage
   - Round and WPM information display
   - Time tracking during training

4. **Results Display**
   - Calculated WPM from actual reading time
   - Session statistics and completion messages
   - Option to practice again with new rounds

## API Endpoints

### Backend Endpoints

#### 1. Prepare Speed Training Session
```
POST /speed-trainer/prepare
Request:
{
  "text": "paragraph text here",
  "speeds": [60, 75, 90]  // Optional, defaults to [60, 75, 90]
}

Response:
{
  "text": "paragraph text here",
  "words": ["word1", "word2", ...],
  "total_words": 100,
  "speeds": [60, 75, 90],
  "intervals": [1000, 800, 667],  // milliseconds per word
  "session_id": "abc12345"
}
```

#### 2. Get Session Data
```
GET /speed-trainer/session/{session_id}

Response:
{
  "text": "paragraph text here",
  "words": ["word1", "word2", ...],
  "total_words": 100,
  "current_round": 0,
  "current_word_index": 5,
  "current_word": "word6",
  "is_paused": false,
  "is_completed": false,
  "rounds": [
    {
      "round_number": 1,
      "wpm": 60,
      "interval_ms": 1000,
      "duration_seconds": 100.0,
      "status": "in_progress"
    },
    ...
  ],
  "session_id": "abc12345"
}
```

#### 3. Perform Session Action
```
POST /speed-trainer/action/{session_id}
Request:
{
  "action": "start|pause|resume|reset|advance_word",
  "session_id": "abc12345"
}

Response:
{
  "action": "advance_word",
  "result": "Advanced to next word",
  "session_data": { ... },
  "success": true
}
```

#### 4. Get Session Statistics
```
GET /speed-trainer/stats/{session_id}

Response:
{
  "total_words": 100,
  "total_rounds": 3,
  "completed_rounds": 1,
  "current_round": 2,
  "total_duration_seconds": 300.5,
  "average_wpm": 75.0,
  "min_wpm": 60,
  "max_wpm": 90,
  "is_completed": false
}
```

#### 5. Submit Reading Results (NEW)
```
POST /speed-trainer/submit-results
Request:
{
  "session_id": "abc12345",
  "elapsed_time_seconds": 45.3
}

Response:
{
  "session_id": "abc12345",
  "total_words": 100,
  "elapsed_time_seconds": 45.3,
  "calculated_wpm": 132.5,
  "status": "completed",
  "message": "Great job! You read 100 words in 45.3 seconds at 133 WPM"
}
```

### Frontend API Functions

#### `submitSpeedTrainerResults(sessionId, elapsedTimeSeconds)`
Submits the actual reading time and receives the calculated WPM.

```typescript
import { submitSpeedTrainerResults } from './api';

try {
  const result = await submitSpeedTrainerResults('session123', 45.3);
  console.log(`Your speed: ${result.calculated_wpm} WPM`);
} catch (error) {
  console.error('Failed to submit results:', error);
}
```

## Architecture & Data Flow

### Setup Flow
1. User initializes training session
2. Frontend calls `POST /speed-trainer/prepare` with paragraph text
3. Backend creates session, splits text into words, calculates intervals
4. Frontend receives session data including all words and timing info

### Training Flow
1. User clicks "Start Training"
2. 3-second countdown begins (3, 2, 1, Go!)
3. Timer starts tracking elapsed time
4. Words highlight sequentially based on `interval_ms`
5. Frontend calls `POST /speed-trainer/action` with "advance_word" action
6. Backend updates word position
7. Process repeats until all words shown

### Completion Flow
1. All words have been highlighted
2. Backend marks session as `is_completed: true`
3. Frontend captures elapsed time duration
4. Frontend calls `POST /speed-trainer/submit-results` with elapsed time
5. Backend calculates: `WPM = (total_words / elapsed_time) * 60`
6. Frontend displays: Words, Time, and Calculated WPM

## How WPM Calculation Works

### Backend Calculation
```
Training Round Speed (Fixed):
Round 1: 60 WPM
Round 2: 75 WPM  
Round 3: 90 WPM

Word Interval = 60000 / WPM (milliseconds)
Round 1: 60000 / 60 = 1000ms per word
Round 2: 60000 / 75 = 800ms per word
Round 3: 60000 / 90 = 667ms per word

Actual Reading Speed:
WPM = (total_words / elapsed_time_seconds) * 60
```

### Example
- 100 words in text
- User completes reading in 45.3 seconds
- Calculated WPM = (100 / 45.3) * 60 = 132.5 WPM

## Component Integration

### SpeedTrainerWidget Props
```typescript
interface SpeedTrainerWidgetProps {
  paragraph: string;      // Text to train on
  isShowing: boolean;     // Show/hide widget
  onClose?: () => void;   // Callback when closing
}
```

### Usage Example
```typescript
import SpeedTrainerWidget from './components/SpeedTrainerWidget';

<SpeedTrainerWidget
  paragraph={selectedParagraph}
  isShowing={showSpeedTrainer}
  onClose={() => setShowSpeedTrainer(false)}
/>
```

## State Management

### Component State
- `sessionId`: Current session identifier
- `session`: Full session data from backend
- `stats`: Session statistics
- `isRunning`: Whether training is active
- `countdown`: Countdown display state (3, 2, 1, Go)
- `elapsedTime`: Tracked elapsed time in seconds
- `completionResult`: Final WPM and stats from backend

### Backend Session Storage
Sessions are stored in memory via `speed_trainer_sessions` dictionary. In production, consider adding:
- Database persistence
- Session timeout handling
- Clean-up of completed sessions

## Time Tracking Implementation

### Frontend Time Management
```typescript
// Start time captured after countdown
startTimeRef.current = Date.now();

// Update elapsed time every 100ms
const elapsed = (Date.now() - startTimeRef.current) / 1000;
setElapsedTime(elapsed);

// On pause: adjust start time for resume
startTimeRef.current = Date.now() - (elapsedTime * 1000);
```

## Styling & UX

### Key Features
- Gradient purple theme for modern appearance
- Large, readable fonts (dyslexia-friendly)
- High contrast for better visibility
- Smooth animations for word highlighting
- Countdown overlay with full-screen effect
- Responsive design for mobile devices

### CSS Classes
- `.speed-trainer-widget`: Main container
- `.word.highlight`: Currently highlighted word
- `.countdown-overlay`: Full-screen countdown
- `.completion-message`: Results display
- `.progress-bar`: Progress tracking

## Error Handling

### Backend Validation
- Empty text validation
- Session not found checks
- Invalid action detection
- WPM greater than 0 requirement

### Frontend Error Display
- Network error messages
- Invalid session handling
- Timeout management (120s for requests)

## Performance Considerations

1. **Word Splitting**: Punctuation is cleaned to avoid display issues
2. **Timer Precision**: Uses `setInterval` for elapsed time (100ms granularity)
3. **Memory**: Sessions stored in memory (suitable for demo/small deployments)
4. **Rendering**: Only highlighted word changes per interval (efficient)

## Future Enhancements

1. **Database Storage**: Persist sessions and results
2. **User Profiles**: Track progress over time
3. **Customizable Speeds**: Allow users to set custom WPM targets
4. **Advanced Analytics**: Detailed reading pattern analysis
5. **Multi-language Support**: Support for different languages
6. **Audio Feedback**: Optional pronunciation guide
7. **Difficulty Levels**: Adaptive speed based on performance
8. **Achievements**: Badges and milestones for motivation

## Testing the Feature

### Quick Test Script
```bash
# Start the backend
cd backend
python app.py

# In another terminal, test with curl
curl -X POST http://localhost:8000/speed-trainer/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog",
    "speeds": [60, 75, 90]
  }'
```

### Frontend Testing
1. Navigate to the application
2. Select a paragraph for speed training
3. Click "Start Training"
4. Watch the 3-second countdown
5. Follow the highlighted words
6. Review your calculated WPM when complete
7. Option to try again with new training sessions

## Troubleshooting

### Common Issues

1. **Session not found error**
   - Ensure backend is running
   - Check session ID is correct
   - Sessions expire if server restarts

2. **Words not highlighting**
   - Check browser console for JS errors
   - Verify interval_ms is being calculated
   - Ensure `isRunning` state is true

3. **Incorrect WPM calculation**
   - Verify elapsed time is being tracked
   - Check that results are submitted with correct time
   - Ensure word count matches what was displayed

4. **Countdown not displaying**
   - Check CSS is loaded
   - Verify countdown-overlay styles exist
   - Check z-index value is high enough

## Summary

The Guided Pace Reading (Speed Trainer) feature provides a complete system for progressive reading speed improvement. Users follow automatically-advancing words at set paces and receive real-time feedback on their actual reading speed. The system combines backend speed management with frontend time tracking for accurate WPM calculation.

