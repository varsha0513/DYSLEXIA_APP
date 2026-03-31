# Learning Journey Progress - 140% Analysis

## Summary
The "Learning Journey" progress metric is calculated in [CourseContext.tsx](frontend/src/contexts/CourseContext.tsx) and displayed in [ProgressTracker.tsx](frontend/src/components/ProgressTracker.tsx). The issue causing 140% progress involves a mismatch between available steps and the completion counter.

---

## Where "Learning Journey" is Displayed

**File**: [frontend/src/components/ProgressTracker.tsx](frontend/src/components/ProgressTracker.tsx#L29-L31)
- **Component**: Shows "Learning Journey" title along with progress percentage
- **Calculation**: Uses `completionPercentage` from CourseContext
- **Display**: `{Math.round(completionPercentage)}%` on line 31
- **Progress Bar**: Width is set to `${completionPercentage}%` on line 39

```tsx
<h2 className="progress-title">Learning Journey</h2>
<div className="progress-percentage">
  {Math.round(completionPercentage)}%
</div>
```

---

## Progress Calculation Formula

**File**: [frontend/src/contexts/CourseContext.tsx](frontend/src/contexts/CourseContext.tsx#L129)

### Current Formula (Line 129):
```tsx
const completionPercentage = (completedCount / COURSE_STEPS.length) * 100;
```

### Current Steps Defined (Lines 25-30):
```tsx
const COURSE_STEPS: CourseStep[] = [
  'reading-assessment',        // Step 1 (index 0)
  'result-analysis',           // Step 2 (index 1)
  'pronunciation-training',    // Step 3 (index 2)
  'eye-focus-test',            // Step 4 (index 3)
  'phrase-training',           // Step 5 (index 4)
];
```

**Result**: Max possible = `(5/5) * 100 = 100%`

---

## Why 140% is Showing

### Root Cause: Mismatch Between Steps

There's a **component-context mismatch**:

1. **Components Using Extra Steps**:
   - [frontend/src/components/AgeSelectionStep.tsx](frontend/src/components/AgeSelectionStep.tsx#L15) - calls `markStepComplete('age-selection')`
   - [frontend/src/components/ReadingSpeedTrainingStep.tsx](frontend/src/components/ReadingSpeedTrainingStep.tsx#L22) - calls `markStepComplete('reading-speed-training')`

2. **CourseContext Definition** (Lines 1-7):
   ```tsx
   export type CourseStep = 
     | 'reading-assessment'
     | 'result-analysis'
     | 'pronunciation-training'
     | 'eye-focus-test'
     | 'phrase-training';
     // Missing: 'age-selection' and 'reading-speed-training'
   ```

### The Problem:

When components call `markStepComplete('age-selection')` or `markStepComplete('reading-speed-training')`, the context:
- ✅ Saves these to localStorage (no type checking on the setter)
- ❌ Doesn't count them in `completedCount` (because they're not TypeScript-valid CourseSteps)
- ❌ Doesn't include them in `COURSE_STEPS.length` denominator

### How This Results in 140%:

If localStorage contains completion data for 7 steps but the denominator only counts 5:
- **Scenario**: localStorage has completions for: age-selection, reading-assessment, result-analysis, pronunciation-training, eye-focus-test, phrase-training, AND reading-speed-training (7 total)
- **Calculation**: Some implementation may count 7 completed but divide by 5 total
- **Result**: `(7/5) * 100 = 140%`

---

## Components/Files Involved

### Display Layer:
| File | Component | Purpose |
|------|-----------|---------|
| [ProgressTracker.tsx](frontend/src/components/ProgressTracker.tsx) | Shows "Learning Journey" title and percentage | Displays progress to user |
| [ProgressTracker.css](frontend/src/components/ProgressTracker.css) | Styling for progress tracker | Visual appearance |

### Calculation Layer:
| File | Purpose |
|------|---------|
| [CourseContext.tsx](frontend/src/contexts/CourseContext.tsx#L129) | Calculates `completionPercentage = (completedCount / COURSE_STEPS.length) * 100` |

### Step Components (Using Inconsistent Step Names):
| File | Step Name Called | Is in CourseContext? |
|------|------------------|----------------------|
| [AgeSelectionStep.tsx](frontend/src/components/AgeSelectionStep.tsx#L15) | `'age-selection'` | ❌ No |
| [ReadingAssessmentStep.tsx](frontend/src/components/ReadingAssessmentStep.tsx) | `'reading-assessment'` | ✅ Yes |
| [ResultAnalysisStep.tsx](frontend/src/components/ResultAnalysisStep.tsx) | `'result-analysis'` | ✅ Yes |
| [PronunciationTrainingStep.tsx](frontend/src/components/PronunciationTrainingStep.tsx) | `'pronunciation-training'` | ✅ Yes |
| [EyeFocusTestStep.tsx](frontend/src/components/EyeFocusTestStep.tsx) | `'eye-focus-test'` | ✅ Yes |
| [PhraseTrainingStep.tsx](frontend/src/components/PhraseTrainingStep.tsx) | `'phrase-training'` | ✅ Yes |
| [ReadingSpeedTrainingStep.tsx](frontend/src/components/ReadingSpeedTrainingStep.tsx#L22) | `'reading-speed-training'` | ❌ No |

---

## Related Styling/Configuration

**File**: [frontend/src/components/ProgressTracker.css](frontend/src/components/ProgressTracker.css)

- Line 27: `.progress-percentage` styling
- Line 237+: Media query adjustments for responsive design
- Progress bar styling uses CSS gradient from accent-primary to accent-secondary
- Progress bar width is dynamically set via inline styles: `width: ${completionPercentage}%`

---

## Data Persistence Issue

**File**: [CourseContext.tsx](frontend/src/contexts/CourseContext.tsx#L53-70)

The context saves completions to localStorage:
```tsx
const savedCompletion = localStorage.getItem('courseStepCompletion');
// and
localStorage.setItem('courseStepCompletion', JSON.stringify(updated));
```

**Problem**: TypeScript doesn't enforce the CourseStep type when reading from localStorage, allowing "invalid" steps like 'age-selection' and 'reading-speed-training' to persist.

---

## How to Identify Current Status

### In Browser DevTools Console:
```javascript
// Check what's in localStorage
JSON.parse(localStorage.getItem('courseStepCompletion'))
// Output might show: 
// {
//   "age-selection": true,
//   "reading-assessment": true,
//   "result-analysis": true,
//   "pronunciation-training": true,
//   "eye-focus-test": true,
//   "phrase-training": true,
//   "reading-speed-training": true
// }
```

### The Calculation Issue:
- **Completed Count** (from Object.values()): 7 items = true
- **COURSE_STEPS.length**: 5 items
- **Result**: `(7/5) * 100 = 140%`

---

## Key Files to Review

1. **Primary**: [frontend/src/contexts/CourseContext.tsx](frontend/src/contexts/CourseContext.tsx) - Contains the calculation formula
2. **Secondary**: [frontend/src/components/ProgressTracker.tsx](frontend/src/components/ProgressTracker.tsx) - Displays the metric
3. **Related**: [frontend/src/components/ReadingSpeedTrainingStep.tsx](frontend/src/components/ReadingSpeedTrainingStep.tsx) - Uses undefined step name
4. **Related**: [frontend/src/components/AgeSelectionStep.tsx](frontend/src/components/AgeSelectionStep.tsx) - Uses undefined step name

---

## Recommendation

To fix the 140% issue, the CourseContext needs to include all steps that are being marked as complete:
- Add `'age-selection'` to CourseStep type and COURSE_STEPS array
- Add `'reading-speed-training'` to CourseStep type and COURSE_STEPS array
- Update step count from 5 to 7
- This will ensure the denominator matches actual completion tracking
