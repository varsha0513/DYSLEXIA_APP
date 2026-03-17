# Authentication System - Verification Checklist

## Pre-Test Checklist

### Backend Setup
- [ ] `pip install bcrypt PyJWT pydantic[email]` executed successfully
- [ ] No import errors when running `python app:app`
- [ ] Database setup script run: `python setup_db.py`
- [ ] Backend starts with: `python -m uvicorn app:app --reload`
- [ ] Backend accessible at http://localhost:8000

### Frontend Setup
- [ ] All new files exist (authAPI.ts, AuthContext.tsx, LoginPage.tsx, SignUpPage.tsx, Dashboard.tsx, AuthPages.css, Dashboard.css)
- [ ] No TypeScript compilation errors
- [ ] Frontend starts with: `npm run dev`
- [ ] Frontend accessible at http://localhost:5173

---

## Test Scenario 1: New User Registration

### Setup
- [ ] Navigate to http://localhost:5173
- [ ] Login page displays

### Signup Form Test
- [ ] Click "Create one here" link at bottom of login form
- [ ] Redirected to signup page

### Form Field Validation
- [ ] Empty form submission shows errors under each field
- [ ] Name field required
- [ ] Email field required
- [ ] Age field must be 5-100
- [ ] Password field shows requirement message (6+ chars, 1 uppercase, 1 number)

### Successful Signup
**Fill form with:**
- Name: Test User
- Email: testuser@example.com
- Age: 12
- Password: TestPass123
- Confirm: TestPass123

- [ ] All fields pass validation
- [ ] "Create Account" button is clickable
- [ ] Clicking button shows "Creating Account..." loading state
- [ ] No error message appears
- [ ] Redirected to dashboard (not login page)

### Dashboard After Signup
- [ ] Dashboard displays "Test User" name
- [ ] Shows "0/7 Completed" progress
- [ ] Progress bar is empty
- [ ] Shows all 7 training steps
- [ ] "Start Training" button visible
- [ ] Logout button visible in top right
- [ ] No error messages

---

## Test Scenario 2: Login with New Account

### Setup
- [ ] Click "Logout" button on dashboard
- [ ] Redirected to login page
- [ ] Login form is clear

### Form Validation
- [ ] Empty email shows error
- [ ] Empty password shows error
- [ ] Invalid email format shows error

### Successful Login
**Enter credentials:**
- Email: testuser@example.com
- Password: TestPass123

- [ ] Both fields pass validation
- [ ] "Sign In" button is clickable
- [ ] Clicking button shows "Signing In..." loading state
- [ ] No error message
- [ ] Redirected to dashboard
- [ ] Dashboard shows "Test User"
- [ ] Previous progress (0/7) still shows (or progress from before)

---

## Test Scenario 3: Demo Account Login

### Setup
- [ ] Ensure logged out (on login page)

### Successful Login
**Use demo credentials:**
- Email: demo@example.com
- Password: Demo123

- [ ] Form accepts credentials
- [ ] No validation errors
- [ ] "Sign In" button enables
- [ ] Clicking shows "Signing In..." state
- [ ] Redirected to dashboard
- [ ] Dashboard displays user information
- [ ] Demo credentials shown on login page (for reference)

---

## Test Scenario 4: Session Persistence

### Setup
- [ ] User logged in (any account)
- [ ] Dashboard displayed

### Page Refresh
- [ ] Refresh browser page (Ctrl+R or Cmd+R)
- [ ] No redirect to login page
- [ ] Dashboard still visible
- [ ] User info still displayed
- [ ] Progress still shows correctly

### Hard Refresh
- [ ] Hard refresh (Ctrl+Shift+R or clear cache)
- [ ] Loading spinner appears briefly
- [ ] Dashboard loads after spinner
- [ ] User session restored
- [ ] No redirect to login

### Browser Close & Reopen
- [ ] Close browser window
- [ ] Reopen browser
- [ ] Visit http://localhost:5173
- [ ] Navigates to dashboard (session persisted)
- [ ] User info displays

---

## Test Scenario 5: Logout Functionality

### Setup
- [ ] User logged in
- [ ] Dashboard displayed
- [ ] Top-right has logout button

### Logout Action
- [ ] Click "Logout" button
- [ ] Loading appears briefly
- [ ] Redirected to login page
- [ ] Login form is clear/fresh
- [ ] No error messages

### Verify Session Cleared
- [ ] Refresh page
- [ ] Still on login page (not dashboard)
- [ ] Session definitely cleared
- [ ] localStorage cleaned

---

## Test Scenario 6: Password Validation Rules

### Test Minimum Length (6 chars)
- [ ] Password "Test12" is accepted (6 chars, has uppercase, has number)
- [ ] Password "Test1" is rejected (5 chars)

### Test Uppercase Requirement
- [ ] Password "testpass123" shows error "must include uppercase"
- [ ] Password "Testpass123" is accepted

### Test Digit Requirement
- [ ] Password "TestPass" shows error "must include number"
- [ ] Password "TestPass1" is accepted

### Test Confirmation Match
- [ ] Password: "TestPass123", Confirm: "TestPass124" shows error
- [ ] Password: "TestPass123", Confirm: "TestPass123" accepted

---

## Test Scenario 7: Email Validation

### Invalid Emails
- [ ] "notanemail" rejected
- [ ] "@example.com" rejected
- [ ] "user@" rejected
- [ ] "user@example" accepted (valid format)

### Valid Emails
- [ ] "user@example.com" accepted
- [ ] "user.name@example.com" accepted
- [ ] "user+tag@example.co.uk" accepted

### Duplicate Prevention
- [ ] Signup with "duplicate@test.com"
- [ ] Logout and attempt signup with same email
- [ ] Error: "Email already registered"
- [ ] No account created

---

## Test Scenario 8: Dashboard Features

### User Information Display
- [ ] Name shows correctly
- [ ] Email shows correctly
- [ ] Age shows correctly
- [ ] Join date shows (created_at timestamp)

### Progress Display
- [ ] Progress counter shows X/7
- [ ] Progress percentage calculated correctly
- [ ] Progress bar fills proportionally

### Training Steps Grid
- [ ] All 7 steps visible:
  1. Age Selection
  2. Reading Assessment
  3. Result Analysis
  4. Pronunciation Training
  5. Eye Focus Test
  6. Phrase Training
  7. Reading Speed Training
- [ ] Each step shows icon, title, description
- [ ] Incomplete steps: no badge
- [ ] Completion badges display correctly

### Navigation
- [ ] Click step card → navigates to that training module
- [ ] "Start Training" button → goes to first step
- [ ] "Continue Training" button → goes to next incomplete step

---

## Test Scenario 9: Error Handling

### Invalid Email Format
- [ ] Signup attempt with "bademail"
- [ ] Error message displays above form
- [ ] Form doesn't submit
- [ ] Error clears on correction

### Network Error Simulation
- [ ] Stop backend server (Ctrl+C)
- [ ] Attempt login
- [ ] Error message displays: "Backend not responding" or similar
- [ ] Restart backend and retry → works

### Incorrect Login Credentials
- [ ] Email: testuser@example.com, Password: WrongPassword
- [ ] Error message: "Invalid email or password"
- [ ] Not redirected to dashboard
- [ ] Can retry with correct credentials

---

## Test Scenario 10: Browser DevTools Verification

### LocalStorage Check (after login)
- [ ] Open DevTools → Application → Storage → LocalStorage
- [ ] Key `authToken` exists with JWT token
- [ ] Key `currentUser` exists with JSON user object
- [ ] Token starts with "eyJ" (JWT format)

### Console Verification
- [ ] No 401/403 errors
- [ ] No CORS errors
- [ ] No "undefined" errors
- [ ] Auth errors clearly logged

### Network Tab Verification
- [ ] Signup: POST /auth/signup → 200 response
- [ ] Login: POST /auth/login → 200 response
- [ ] Me: GET /auth/me → 200 response with Authorization header
- [ ] Each response includes access_token

---

## Test Scenario 11: Microphone Integration Test

### Training with Authentication
- [ ] Logged in on dashboard
- [ ] Start training (click any step)
- [ ] Try to use microphone features (Step 4, 5, or 6)
- [ ] Microphone permissions requested
- [ ] Recording works normally
- [ ] No auth-related errors in console

### Token with Training APIs
- [ ] Check Network tab during training
- [ ] Verify APIs don't require Authorization header (backward compatible)
- [ ] If future APIs need auth, token should be available via useAuth hook

---

## Performance Checks

### Load Times
- [ ] Dashboard loads in < 2 seconds
- [ ] Form submission (login/signup) completes in < 3 seconds
- [ ] Page refresh with session restore < 1 second

### Memory Leaks
- [ ] Leave dashboard open for 5 minutes
- [ ] DevTools Memory tab: no continuous growth
- [ ] Browser not becoming sluggish

---

## Security Spot Checks

### Password Security
- [ ] Database: User's password never visible as plain text
- [ ] Network: Password sent only over HTTP (HTTPS in production)
- [ ] JavaScript memory: Password not logged or stored after use

### Token Security
- [ ] Token not in URL (only in localStorage and Authorization header)
- [ ] Token sent only in Authorization header for /auth/me
- [ ] Token includes expiration (30 days)

---

## Summary

**Pass Criteria:** All test scenarios complete without critical errors

- **Critical Issues:** Auth not working, errors on page load, crashes during signup/login
- **Major Issues:** Some validation not working, session not persisting, token-related errors
- **Minor Issues:** UI non-responsive, typos, styling issues, console warnings

**Testing Time Estimate:** 30-45 minutes for full verification

**First Quick Test (5 minutes):**
1. [ ] Backend starts without errors
2. [ ] Frontend starts without errors  
3. [ ] Can signup with new account
4. [ ] Can login with that account
5. [ ] Dashboard shows after login

---

## Success Indicator

✅ System is ready when:
- User can sign up → login → access dashboard → see progress
- Session persists after refresh
- Logout clears session
- All validation works
- No console errors related to auth
