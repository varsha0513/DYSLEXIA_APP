# Streak Feature Implementation Guide

## Overview
The streak feature tracks daily task completion across the 5 training steps. Users build a streak by completing all 5 steps each day, and lose the streak if they miss a day.

## How It Works

### Streak Logic
1. **Day 1**: User completes all 5 steps → Streak = 1
2. **Day 2**: User completes all 5 steps → Streak = 2
3. **Day 3**: User skips training → Streak resets to 0
4. **Day 4 onwards**: Can rebuild streak again from 1

### Key Fields in Database
- `current_streak` (Integer): Current consecutive days of completion (0-∞)
- `best_streak` (Integer): Highest streak achieved
- `last_completed_date` (Date): Last day all 5 steps were completed

## Backend Implementation

### 1. Database Schema Changes
Run the migration SQL to add streak fields:
```sql
ALTER TABLE users ADD COLUMN current_streak INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN best_streak INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN last_completed_date DATE;
CREATE INDEX idx_users_last_completed_date ON users(last_completed_date);
```

**File**: `backend/migrate_add_streak_fields.sql`

### 2. API Endpoints

#### POST `/training/daily-checkpoint`
Marks daily completion and updates user's streak.

**Request Header**:
```
Authorization: Bearer {token}
```

**Response**:
```json
{
  "current_streak": 5,
  "best_streak": 8,
  "streak_updated": true,
  "message": "🔥 Streak continues! 5 days",
  "last_completed_date": "2026-03-17"
}
```

**Streak Update Logic**:
- First time completing: Set streak = 1, best_streak = 1
- Same day completion: No change (message: "Already completed today")
- Next day completion: Increment streak by 1, update best_streak if needed
- Missed days: Reset streak to 1 with warning message

#### GET `/training/streak-info`
Retrieves current streak information and daily progress.

**Request Header**:
```
Authorization: Bearer {token}
```

**Response**:
```json
{
  "current_streak": 5,
  "best_streak": 8,
  "completed_steps_today": 3,
  "total_daily_steps": 5,
  "last_completed_date": "2026-03-17",
  "will_lose_streak": true,
  "days_until_streak_loss": 1
}
```

### 3. Modified Files
- **models.py**: Added 3 new columns to User model
- **schemas.py**: Updated UserResponse with streak fields; added DailyCheckpointResponse and StreakInfoResponse
- **app.py**: Added 2 new endpoints with complete streak logic

## Frontend Implementation

### 1. Streak API Client
**File**: `frontend/src/api/StreakAPI.ts`

Provides methods:
- `getStreakInfo(token)`: Fetch current streak and daily progress
- `markDailyCompletion(token)`: Call when all 5 steps are completed

### 2. StreakDisplay Component
**File**: `frontend/src/components/StreakDisplay.tsx`

Features:
- 🔥 Streak Card: Displays current streak number and best streak
- Daily Progress: Shows X of 5 tasks completed with visual progress bar
- Streak Warning: Alerts user when at risk of losing streak
- Streak Success: Celebrates completion when all 5 steps done today

**CSS File**: `frontend/src/components/StreakDisplay.css`

Dark theme support with CSS variables and responsive design.

### 3. Dashboard Integration
**File**: `frontend/src/components/Dashboard.tsx`

- Added StreakDisplay component above the progress section
- Displays streak card and daily progress to user on login

### 4. Automatic Daily Checkpoint
**File**: `frontend/src/components/CourseLayout.tsx`

- Automatically calls `/training/daily-checkpoint` when all 5 steps complete
- Shows alert with streak update and current streak number
- Prevents duplicate calls using `checkpointCalled` flag

### 5. Updated User Type
**File**: `frontend/src/utils/authAPI.ts`

Added streak fields to User interface:
```typescript
interface User {
  // ... existing fields
  current_streak: number;
  best_streak: number;
  last_completed_date: string | null;
}
```

## User Experience Flow

1. **Dashboard View**: User sees streak card showing:
   - Current streak count with fire emoji (🔥)
   - Best streak achieved
   - Daily progress (3 of 5 tasks)
   - Risk warning if incomplete

2. **Training Session**: User works through 5 steps:
   - Step 1: Reading Assessment
   - Step 2: Result Analysis
   - Step 3: Pronunciation Training
   - Step 4: Eye Focus & Guided Reading
   - Step 5: Chunk Reading (Phrase Training)

3. **Completion**: When all 5 steps finish:
   - Automatic daily checkpoint call
   - Alert shows streak message and count
   - Next day, user can continue building streak

## Setup Instructions

### Step 1: Database Migration
```bash
# Connect to your database
psql -U postgres -d dyslexia_app < backend/migrate_add_streak_fields.sql
```

### Step 2: Backend Restart
```bash
cd backend
python app.py
```

### Step 3: Frontend Update
No additional setup needed - components are already integrated.

### Step 4: Test
1. Log in to the app
2. Complete all 5 training steps
3. Check the alert message confirming streak update
4. Go back to dashboard to see updated streak display

## Testing Scenarios

### Scenario 1: First Completion
- New user completes all 5 steps
- Expected: Current streak = 1, best_streak = 1
- Message: "🔥 Streak started! 1 day"

### Scenario 2: Continuous Completion
- User completes all 5 steps on day 1, 2, 3
- Expected: Streak increments 1→2→3
- Best streak updates if exceeding previous

### Scenario 3: Missing a Day
- User completes day 1, misses day 2, does training on day 3
- Expected: Streak resets to 1
- Message: "⚠️ Streak reset! Starting fresh at 1 day"

### Scenario 4: Same Day Multiple Trains
- User completes all 5 steps, tries again same day
- Expected: Streak unchanged, message: "Already completed today"

## Customization Options

### Change Streak Colors
Edit `StreakDisplay.css`:
```css
/* Gradient colors for streak card */
.streak-card {
  background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
}

/* Progress bar colors */
.progress-fill {
  background: linear-gradient(90deg, #4CAF50, #81c784);
}
```

### Change Streak App Count
In `StreakInfoResponse` schema, change:
```python
total_daily_steps: int = 5  # Change to desired number
```

### Disable Automatic Checkpoint
Remove or comment out the `useEffect` in `CourseLayout.tsx`:
```typescript
// useEffect(() => { ... }, [stepCompletion, token, checkpointCalled]);
```

## Common Issues

### Issue: Streak not updating
**Solution**: Ensure `/training/daily-checkpoint` endpoint is called when all 5 steps complete. Check browser console for API errors.

### Issue: Streak shows 0 for existing users
**Solution**: Existing users need data migration. Run SQL update:
```sql
UPDATE users SET current_streak = 0, best_streak = 0 WHERE current_streak IS NULL;
```

### Issue: Dark theme styling broken
**Solution**: Ensure CSS variables are defined in your theme CSS file (--primary-bg, --text-primary, etc.)

## Future Enhancements

1. **Streak Notifications**: Push notifications when streak is about to be lost
2. **Streak Milestones**: Special badges for 7, 30, 100+ day streaks
3. **Team Streaks**: Group streaks where multiple users compete
4. **Streak Freeze**: Allow 1 or 2 "freeze" days per month to maintain streak
5. **Gamification**: Points/rewards for longer streaks
6. **Streak Analytics**: Charts showing streak history over time

## Database Queries

### Check user streaks
```sql
SELECT username, current_streak, best_streak, last_completed_date 
FROM users 
ORDER BY current_streak DESC;
```

### Find users who might lose streak
```sql
SELECT username, current_streak, last_completed_date, 
       CURRENT_DATE - last_completed_date as days_since
FROM users 
WHERE last_completed_date < CURRENT_DATE - 1 
AND current_streak > 0;
```

### Reset all streaks
```sql
UPDATE users SET current_streak = 0;
```

---

**Implementation Date**: March 17, 2026  
**Status**: ✅ Complete and Ready for Testing
