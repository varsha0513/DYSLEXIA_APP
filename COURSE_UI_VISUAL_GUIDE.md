# Course UI - Visual Layout & Design Reference

## Desktop Layout (1024px and above)

```
┌────────────────────────────────────────────────────────────────────────┐
│                      NAVIGATION BAR (70px height)                      │
├────────────────┬──────────────────────────────────────────────────────┤
│                │                                                      │
│   SIDEBAR      │              MAIN CONTENT AREA                      │
│  (300px)       │                                                      │
│                │  ┌──────────────────────────────────────────────┐   │
│ Learning       │  │ 📖 Reading Assessment                        │   │
│ Journey        │  │ Let's assess your reading skills            │   │
│                │  │ Description of the step...                   │   │
│ Progress: 33%  │  │                                              │   │
│ ▓▓░░░░░░░░    │  └──────────────────────────────────────────────┘   │
│                │                                                      │
│ ✔ Step 1      │  ┌──────────────────────────────────────────────┐   │
│ ➤ Step 2      │  │                                              │   │
│ ⬜ Step 3     │  │   Step Content (ReadingTask, etc.)           │   │
│ ⬜ Step 4     │  │                                              │   │
│ ⬜ Step 5     │  │                                              │   │
│ ⬜ Step 6     │  │                                              │   │
│                │  │                                              │   │
│ 📚 Keep going! │  │                                              │   │
│                │  └──────────────────────────────────────────────┘   │
│                │                                                      │
│                ├──────────────────────────────────────────────────────┤
│                │  Previous | Step 2 of 6 [▓▓░░░░░] | Next →        │
│                │  Button   | Progress Bar         | Button       │
└────────────────┴──────────────────────────────────────────────────────┘
```

## Responsive Tablet Layout (768px - 1024px)

```
┌────────────────────────────────────────────────────┐
│            NAVIGATION BAR                          │
├────────────────────────────────────────────────────┤
│ SIDEBAR (narrower, 280px)                          │
├────────────────────────────────────────────────────┤
│                                                    │
│           MAIN CONTENT AREA (full width)          │
│                                                    │
│           Step Content                             │
│                                                    │
├────────────────────────────────────────────────────┤
│  Previous | Step 2 of 6 | Next →                  │
└────────────────────────────────────────────────────┘
```

## Mobile Layout (below 768px)

```
┌──────────────────────────┐
│   NAVIGATION BAR         │
├──────────────────────────┤
│ SIDEBAR (Horizontal)     │
│ [Progress: 33%] [Steps]  │
├──────────────────────────┤
│                          │
│   MAIN CONTENT AREA      │
│   (Full width)           │
│                          │
│   Step Content           │
│                          │
├──────────────────────────┤
│ [Prev] [Next →]          │
│ (Stacked buttons)        │
└──────────────────────────┘
```

## Sidebar - Progress Tracker

### Component Structure

```
┌──────────────────────────┐
│ Learning Journey   33%   │  ← Title + Percentage
├──────────────────────────┤
│ ▓▓░░░░░░░░             │  ← Progress Bar (gradient)
├──────────────────────────┤
│ ✔ Age Selection    Step 1│  ← Completed Step
│   (Completed)      of 6  │
│                          │
│ ➤ Reading Assess.  Step 2│  ← Current Step (highlighted)
│   (Current)        of 6  │
│                          │
│ ⬜ Result Analys.  Step 3│  ← Upcoming Step
│   (Locked)         of 6  │
│                          │
│ ⬜ Pronunciation   Step 4│
│   (Locked)         of 6  │
│                          │
│ ⬜ Speed Training  Step 5│
│   (Locked)         of 6  │
│                          │
│ ⬜ Eye Focus Test  Step 6│
│   (Locked)         of 6  │
├──────────────────────────┤
│ 📚 Keep going!          │  ← Motivational Badge
└──────────────────────────┘
```

### Step Indicator States

**Completed Step** (Green)
```
┌─────────────────────┐
│ ✔         Age Selection    │
│           (Completed)      │
│           Step 1 of 6      │
│ ← Green checkmark          │
│ ← Green background         │
│ ← Green border             │
└─────────────────────┘
```

**Current Step** (Blue/Purple)
```
┌─────────────────────┐
│ ➤         Reading Assessment│
│           (Current)        │
│           Step 2 of 6      │
│ ← Pulsing arrow            │
│ ← Blue gradient bg         │
│ ← Blue highlighted border  │
│ ← Shadow effect            │
└─────────────────────┘
```

**Upcoming/Disabled Step** (Grey)
```
┌─────────────────────┐
│ ⬜ Result Analysis    │
│  (Locked)          │
│  Step 3 of 6       │
│ ← Grey box icon    │
│ ← Grey text        │
│ ← No hover effect  │
│ ← Cursor: not-allowed │
└─────────────────────┘
```

## Step Content - Header Component

```
┌────────────────────────────────────────────────┐
│  📖   Reading Assessment                       │
│       Let's assess your reading skills        │
│       Description: Please read the paragraph   │
│       below clearly and at your own pace...   │
└────────────────────────────────────────────────┘
      ↑
   Emoji Icon
   (80x80px)
   
   Gradient background
   Subtle border
   Rounded corners
```

## Bottom Navigation - Course Navigation

```
┌────────────────────────────────────────────────┐
│  ← Previous | Step 2 of 6 | Next Step →       │
│   Button    ║ [▓▓░░░░░]  ║ Button             │
│             ║ Progress  ║                     │
│             ║ Bar       ║                     │
└────────────────────────────────────────────────┘
```

### Button States

**Enabled State**
```
┌──────────────┐
│ ← Previous   │  ← White/light background
│              │  ← Dark text
│              │  ← Border outline
│              │  ← Hover: Gradient bg + shadow
│              │  ← Active: Slightly depressed
└──────────────┘
```

**Disabled State**
```
┌──────────────┐
│ ← Previous   │  ← Grey background
│              │  ← Grey text
│              │  ← Opacity: 0.5
│              │  ← Cursor: not-allowed
│              │  ← No hover effect
└──────────────┘
```

## Step Components - Content Panels

### Example: Reading Assessment Step

```
┌─────────────────────────────────────────────┐
│ StepHeader: 📖 Reading Assessment           │
│            "Let's assess your reading..."   │
├─────────────────────────────────────────────┤
│                                             │
│  ReadingTask Component                      │
│  ┌───────────────────────────────────────┐ │
│  │ [Paragraph text displayed here]       │ │
│  │                                       │ │
│  │ [Recording controls]                  │ │
│  │ [Timer: 00:45]                        │ │
│  │ [AudioAura effect (optional)]          │ │
│  └───────────────────────────────────────┘ │
│                                             │
├─────────────────────────────────────────────┤
│ Reading Tips (3-column grid)                │
│ ┌─────────┬─────────┬─────────┐            │
│ │🎙️Micro │📍Quiet  │⏱️ Pace  │            │
│ │Working? │Environment│Comfor │            │
│ │         │         │table   │            │
│ └─────────┴─────────┴─────────┘            │
└─────────────────────────────────────────────┘
```

### Example: Eye Focus Test Step

```
┌─────────────────────────────────────────────┐
│ StepHeader: 👁️ Eye Focus Training            │
│            "Watch & follow each word..."    │
├─────────────────────────────────────────────┤
│ Reading Speed: [Slow] [Medium*] [Fast]     │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │ The  quick  [BROWN*]  fox  jumps   │  │
│  │ over  the  lazy  dog               │  │
│  └─────────────────────────────────────┘  │
│        ↑ Highlighted word with scale      │
│        ↑ Gradient background              │
│        ↑ Pulse animation                  │
│                                             │
│ Progress: [▓▓▓▓░░░░░] 8/45 words          │
│                                             │
│         [▶ Start] [↻ Restart]              │
│                                             │
├─────────────────────────────────────────────┤
│ Tips: Keep eyes on the highlighted word... │
│ - Read at different speeds...              │
│ - Practice daily...                        │
└─────────────────────────────────────────────┘
```

## Color Scheme Reference

### Primary Colors
- **Accent Primary** (Purple/Blue): #667eea
  - Used for: Current step, buttons, highlights
  - RGB: rgb(102, 126, 234)

- **Accent Secondary** (Purple): #764ba2
  - Used for: Gradients, emphasis
  - RGB: rgb(118, 75, 162)

- **Success** (Green): #4caf50
  - Used for: Completed steps, success messages
  - RGB: rgb(76, 175, 80)

### Background Colors
- **Primary**: #ffffff (white)
- **Secondary**: #f5f5f5 (light grey)
- **Tertiary**: #efefef (medium grey)

### Text Colors
- **Primary**: #1a1a1a (dark)
- **Secondary**: #666666 (medium grey)
- **Tertiary**: #999999 (light grey)

### Info/Warning/Error
- **Info**: #e3f2fd (light blue background) + #2196f3 (blue border)
- **Warning**: #fff3e0 (light orange bg) + #ff9800 (orange border)
- **Error**: #ffebee (light red bg) + #f44336 (red border)
- **Success**: #e8f5e9 (light green bg) + #4caf50 (green border)

## Typography

### Font Sizes
- **Step Title**: 1.8rem (28.8px) - Bold
- **Subtitle**: 1.1rem (17.6px) - Semi-bold
- **Body Text**: 0.95-1rem (15.2-16px) - Regular
- **Small Text**: 0.85rem (13.6px) - Regular
- **Labels**: 0.75-0.9rem (12-14.4px) - Semi-bold

### Font Weights
- **Bold**: 700
- **Semi-bold**: 600
- **Regular**: 400-500

### Line Heights
- **Headings**: 1.2
- **Body**: 1.5-1.6
- **Compact**: 1.3-1.4

## Spacing Scale

- **xs**: 4px
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 20px
- **2xl**: 24px
- **3xl**: 32px

## Border Radius

- **Small**: 6px
- **Medium**: 8px
- **Large**: 12px

## Shadow Definitions

- **Light**: 0 2px 8px rgba(0, 0, 0, 0.1)
- **Medium**: 0 4px 12px rgba(0, 0, 0, 0.15)
- **Heavy**: 0 8px 24px rgba(0, 0, 0, 0.2)

## Animation Timings

- **Fast**: 0.2s
- **Standard**: 0.3s
- **Slow**: 0.5-0.6s
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1) (Material Design timing)

---

**Design System Version**: 1.0  
**Last Updated**: March 2026  
**Dyslexia-Friendly**: ✓ Verified
