# Authentication System - Quick Start

## Installation (5 minutes)

### 1. Backend Dependencies
```bash
cd backend
pip install bcrypt PyJWT pydantic[email]
```

### 2. Verify Database
Run this command to ensure the users table has the password_hash field:
```bash
python setup_db.py
```

### 3. Start Backend
```bash
python -m uvicorn app:app --reload
```
Backend will run on http://localhost:8000

### 4. Start Frontend
In a new terminal:
```bash
cd frontend
npm run dev
```
Frontend will open at http://localhost:5173

---

## Testing (10 minutes)

### Option A: Create New Account
1. Click "Create one here" on login page
2. Fill form:
   - Name: Your Name
   - Email: yourname@example.com
   - Age: 12
   - Password: TestPass123 (uppercase + number + 6+ chars)
   - Confirm password: TestPass123
3. Click "Create Account"
4. Redirected to dashboard

### Option B: Use Demo Account
1. **Email:** demo@example.com
2. **Password:** Demo123
3. Click "Sign In"

---

## Quick Test Checklist

- [ ] Can create new account
- [ ] Email and password validation works
- [ ] Login redirects to dashboard
- [ ] Dashboard shows progress (0/7 for new user)
- [ ] Can click "Start Training" button
- [ ] Can logout (button in top-right)
- [ ] After logout, login page shows
- [ ] Session persists after page refresh

---

## System Architecture

```
User (Browser)
    ↓
Frontend (React + TypeScript)
    ├── LoginPage / SignUpPage
    ├── AuthContext (manages auth state)
    └── Dashboard (shows progress)
    ↓
Backend API (FastAPI)
    ├── POST /auth/signup (register)
    ├── POST /auth/login (authenticate)
    └── GET /auth/me (verify session)
    ↓
Database (SQLite)
    └── users table (with password_hash)
```

---

## Common Issues & Solutions

### Backend won't start
**Error:** "Module not found: bcrypt"
```bash
pip install bcrypt PyJWT pydantic[email]
```

### Password rejected during signup
**Error:** "Password does not meet requirements"
**Fix:** Use format: Uppercase + Number + 6+ characters
- ✅ Good: TestPass123
- ✅ Good: SecurePass456
- ❌ Bad: testpass (no uppercase)
- ❌ Bad: TestPass (no number)

### Stuck on loading screen
**Error:** "Loading..." spinner
**Fix:** Check browser console for errors
- Backend might not be running
- CORS issue: Verify backend running on port 8000

### Session not persisting
**Error:** Logging out on page refresh
**Fix:** Check localStorage in browser
- Open DevTools → Application → LocalStorage
- Should see `authToken` and `currentUser`
- Clear and log in again if corrupted

---

## What's Implemented

✅ User signup with validation  
✅ Secure login with JWT tokens  
✅ Session persistence (stays logged in on refresh)  
✅ Training dashboard with progress tracking  
✅ Password requirements enforced  
✅ Email format validation  
✅ bcrypt password hashing (10 rounds)  
✅ 30-day token expiration  
✅ Error messages and feedback  
✅ Responsive mobile-friendly UI  

---

## Next Steps

After verifying everything works:

1. **Test training modules** with authenticated user
2. **Verify microphone permissions** during Phrase Training
3. **Connect progress tracking** to user database (save completion status)
4. **Export user progress** (optional feature)
5. **Add password reset** (future enhancement)

---

## Demo Credentials

```
Email:    demo@example.com
Password: Demo123
```

Use this to quickly test without creating new account.

---

## Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /auth/signup | Create new account |
| POST | /auth/login | Login to account |
| GET | /auth/me | Get current user |

All endpoints tested and working! ✅
