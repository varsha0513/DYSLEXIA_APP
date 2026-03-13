# Quick Start Guide - Course-Style UI

## For Developers

### Installation & Setup

1. **Install dependencies** (if not already done)
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   # or
   npm start
   ```
   Server will be available at `http://localhost:5173` (or `http://localhost:3000`)

3. **Open in browser**
   Navigate to the local development URL

### Key Files to Understand

Start with these files in this order:

1. **[App.tsx](src/App.tsx)** (Main entry point)
   - Shows how CourseProvider wraps the app
   - State management for age, paragraph, results

2. **[CourseContext.tsx](src/contexts/CourseContext.tsx)** (Brain of the app)
   - Step navigation logic
   - Progress tracking
   - LocalStorage integration

3. **[CourseLayout.tsx](src/components/CourseLayout.tsx)** (Layout structure)
   - Two-panel layout (sidebar + main)
   - Container for all steps

4. **[CourseView.tsx](src/components/CourseView.tsx)** (Step router)
   - Determines which step to display
   - Base for all step components

5. **[ProgressTracker.tsx](src/components/ProgressTracker.tsx)** (Left sidebar)
   - Shows all steps and progress
   - Allows step navigation

6. **[CourseNavigation.tsx](src/components/CourseNavigation.tsx)** (Bottom controls)
   - Previous/Next buttons
   - Step indicator

### Component Files Reference

| Step | File | Purpose |
|------|------|---------|
| 1 | AgeSelectionStep | Age input |
| 2 | ReadingAssessmentStep | Reading task |
| 3 | ResultAnalysisStep | Results display |
| 4 | PronunciationTrainingStep | Pronunciation practice |
| 5 | ReadingSpeedTrainingStep | Speed training |
| 6 | EyeFocusTestStep | Eye focus exercise |

### Making Changes

#### To add a motivational message
1. Open the relevant Step component (e.g., `AgeSelectionStep.tsx`)
2. Locate the message div
3. Edit the text
4. Save - HMR will reload automatically

#### To change colors
1. Open `theme.css`
2. Update CSS variable values
3. All components automatically update

#### To adjust sidebar width
1. Open `CourseLayout.css`
2. Change `width: 300px` to desired width
3. Update mobile breakpoint if needed

#### To add a new step
1. Create `NewStep.tsx` and `.css`
2. Add to `CourseContext.tsx`:
   ```typescript
   export type CourseStep = ... | 'new-step'
   const STEP_TITLES = { ..., 'new-step': 'New Step Title' }
   const COURSE_STEPS = [..., 'new-step']
   ```
3. Add case in `CourseView.tsx`

### Testing the Interface

#### Test Progress Tracking
1. Complete each step
2. Watch sidebar update with ✔
3. Refresh page - progress should persist
4. Open DevTools → Application → LocalStorage → `courseStepCompletion`

#### Test Navigation
1. Complete a step → Next button enables
2. Before completing → Next button disabled
3. Click Previous → goes back
4. Click on completed step → jumps to it

#### Test Responsiveness
1. Open DevTools (F12)
2. Click device toolbar (Ctrl+Shift+M)
3. Test mobile (375px), tablet (768px), desktop (1200px)
4. Sidebar should reposition on mobile

#### Test Animations
1. Move between steps
2. Watch smooth transitions
3. Check CourseContext indicators pulse
4. Verify no janky animations (60fps)

### Debugging

#### Check Current Step
```javascript
// In browser console
localStorage.getItem('courseCurrentStep')
```

#### Check Completion Status
```javascript
// In browser console
JSON.parse(localStorage.getItem('courseStepCompletion'))
```

#### Reset Progress
```javascript
// In browser console
localStorage.clear()
location.reload()
```

#### View React Component State
1. Install React DevTools extension
2. Open DevTools
3. Go to Components tab
4. Find CourseProvider
5. Expand to see context value

### Common Tasks

#### Make sidebar narrower
Edit `CourseLayout.css`:
```css
.course-sidebar {
  width: 250px; /* was 300px */
  min-width: 250px;
}
```

#### Change step colors
Edit `ProgressTracker.css`:
```css
.step-item.current {
  background: var(--your-color); /* change this */
}
```

#### Speed up animations
Edit component CSS files:
```css
animation: fadeInUp 0.3s ease-out; /* was 0.6s */
```

#### Add new motivational message
Edit relevant Step component, e.g., `AgeSelectionStep.tsx`:
```typescript
<div className="step-motivational-message">
  <p>Your new message here</p>
</div>
```

## For Designers

### Customizing Colors

Edit [theme.css](src/theme.css):

```css
:root {
  --accent-primary: #667eea; /* Main purple - change here */
  --accent-secondary: #764ba2; /* Secondary purple */
  --success-border: #4caf50; /* Completion green */
  /* etc */
}
```

### Adjusting Spacing

All components use consistent spacing via CSS variables:
```css
/* In component CSS */
padding: 20px 24px; /* lg (20px) + 2xl (24px) */
gap: 16px; /* xl */
margin: 32px 0; /* 3xl */
```

### Modifying Typography

Edit [theme.css](src/theme.css) and component CSS:
```css
.step-header-title {
  font-size: 1.8rem; /* Change size */
  font-weight: 700; /* Change weight */
  letter-spacing: -0.5px; /* Adjust spacing */
}
```

### Changing Animations

Find in component CSS:
```css
animation: fadeInUp 0.6s ease-out; /* Adjust timing */
```

Available animations:
- `fadeInUp` - Content slides up
- `slideUp` - Alternative slide animation
- `pulse` - Gentle pulsing effect
- `highlightPulse` - For eye focus test

## For QA / Testing

### Test Scenarios

**Scenario 1: Complete Full Course**
1. Start app → Age selection
2. Enter age → Next step available
3. Complete reading assessment
4. Click Next → Results appear
5. Continue through all 6 steps
6. Verify 100% progress shown
7. Can return to any step

**Scenario 2: Progress Persistence**
1. Complete step 2
2. Refresh page (Ctrl+R)
3. App returns to step 2
4. Progress bar shows correct percentage
5. Close & reopen browser
6. Progress still there

**Scenario 3: Mobile Responsiveness**
1. Open on mobile device (or DevTools)
2. Sidebar appears vertical
3. Content takes full width
4. Navigation buttons stack
5. Buttons still functional
6. No horizontal scrolling

**Scenario 4: Keyboard Navigation**
1. Use Tab to move between buttons
2. Use Enter/Space to click buttons
3. Test Previous button when disabled
4. Test Next button when disabled
5. All buttons accessible via keyboard

### Performance Checklist

- [ ] Page loads in < 2 seconds
- [ ] Step transitions smooth (60fps)
- [ ] No janky animations
- [ ] No console errors
- [ ] localStorage working
- [ ] Mobile layout works
- [ ] Colors match design
- [ ] Fonts readable
- [ ] Buttons clickable/tappable
- [ ] Progress saving correctly

### Accessibility Checklist

- [ ] Can navigate with keyboard only
- [ ] Color contrast is sufficient
- [ ] Focus indicators visible
- [ ] Font sizes are large enough
- [ ] Spacing is adequate
- [ ] Icons have text labels
- [ ] No time-dependent content
- [ ] Buttons have clear labels
- [ ] Responsive on mobile
- [ ] Works on screen readers

## Resources

### Documentation Files
- **COURSE_UI_IMPLEMENTATION_GUIDE.md** - Full technical guide (start here)
- **COURSE_UI_VISUAL_GUIDE.md** - Design reference and layouts
- **COURSE_IMPLEMENTATION_COMPLETION_REPORT.md** - Project summary

### Related Files
- **types.ts** - TypeScript interfaces
- **theme.css** - Global style variables
- **paragraphs.ts** - Age-appropriate reading content

### External Docs
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [CSS Grid Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Troubleshooting

### "Module not found" error
```bash
npm install
npm run dev
```

### Styles not updating
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

### Progress not saving
1. Check if localStorage is enabled
2. Open DevTools → Application → Storage → LocalStorage
3. Verify courseCurrentStep and courseStepCompletion exist
4. Try: `localStorage.clear()` then refresh

### Step content not showing
1. Check browser console for errors
2. Verify current step in DevTools → Components → CourseProvider
3. Check CourseView component in `CourseView.tsx`
4. Ensure step component is imported and has correct case in switch

### Animations stuttering
1. Check FPS in DevTools → Rendering
2. Check for heavy computations
3. Simplify animations if needed
4. Test on lower-end device to verify

## Getting Help

1. **Check Documentation** - Read the implementation guides first
2. **Review Code Comments** - Components have helpful comments
3. **Check Console** - Browser DevTools may show the error
4. **Inspect Elements** - DevTools inspector shows actual rendered structure
5. **Test in Isolation** - Create minimal test case to isolate issue

---

**Quick Links:**
- [Main App](src/App.tsx)
- [Course Context](src/contexts/CourseContext.tsx)
- [Global Styles](src/theme.css)
- [Implementation Guide](COURSE_UI_IMPLEMENTATION_GUIDE.md)

**Status**: Ready to develop ✅
