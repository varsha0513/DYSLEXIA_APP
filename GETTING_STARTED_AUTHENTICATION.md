# Getting Started - Authentication System

Complete guide to set up and test the new authentication system.

## Time Estimate: 15-20 minutes

---

## Step 1: Install Backend Dependencies (2 minutes)

Open terminal and navigate to backend directory:

```bash
cd backend
```

Install required Python packages:

```bash
pip install bcrypt PyJWT pydantic[email]
```

**Verify installation:**
```bash
python -c "import bcrypt, jwt, pydantic; print('✓ All dependencies installed')"
```

Expected output: `✓ All dependencies installed`

---

## Step 2: Verify Database Setup (1 minute)

The database should already have the users table with password_hash field. To verify:

```bash
python -c "from models import Base, engine, User; print(User.__table__.columns.keys())"
```

You should see output including: `'password_hash'` in the column list

---

## Step 3: Start Backend Server (1 minute)

```bash
python -m uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Leave this running!** Open a new terminal for the next step.

---

## Step 4: Start Frontend Development Server (1 minute)

In a new terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5173/
```

The app should automatically open in your browser at http://localhost:5173

---

## Step 5: Test Signup (3 minutes)

You should see the **login page** with:
- Email and password input fields
- "Don't have an account? Sign up" link
- Demo credentials displayed

### Click "Sign up" link

You should see the **signup page** with:
- Name, Email, Age, Password, Confirm Password fields
- Password requirements displayed below password field

### Fill signup form:

| Field | Value |
|-------|-------|
| Name | Test User |
| Email | testuser@example.com |
| Age | 12 |
| Password | TestPass123 |
| Confirm Password | TestPass123 |

### Click "Create Account"

Button should show "Creating Account..." loading state.

### Expected result:
- Redirected to **dashboard** (not login page)
- Dashboard shows:
  - Your name "Test User"
  - Email "testuser@example.com"
  - "0/7 Completed" progress
  - Empty progress bar
  - All 7 training steps listed

---

## Step 6: Test Logout and Login (3 minutes)

### Click "Logout" button (top-right of dashboard)

You should return to the **login page**.

### Try login with wrong password:

| Field | Value |
|-------|-------|
| Email | testuser@example.com |
| Password | WrongPassword |

Click "Sign In"

You should see **red error banner**: "Invalid email or password"

### Try login with correct password:

| Field | Value |
|-------|-------|
| Email | testuser@example.com |
| Password | TestPass123 |

Click "Sign In"

Button should show "Signing In..." loading state.

### Expected result:
- Redirected to **dashboard**
- Shows same user info and progress as before

---

## Step 7: Test Session Persistence (2 minutes)

### Refresh the page (Ctrl+R or Cmd+R)

Expected:
- Brief loading spinner appears
- Dashboard loads (not login page)
- You remain logged in

### Close browser tab and reopen

1. Close current browser tab
2. Give browser a moment
3. Go back to http://localhost:5173

Expected:
- You are still logged in
- Dashboard shows your info and progress
- Session persisted from localStorage

---

## Step 8: Test Demo Account (2 minutes)

### Click "Logout" to return to login

### Use demo credentials:

| Field | Value |
|-------|-------|
| Email | demo@example.com |
| Password | Demo123 |

Click "Sign In"

### Expected result:
- Redirected to dashboard
- Shows demo user account (if it was created)
- See progress

---

## Troubleshooting

### Problem: "Backend not responding"
**Solution:** 
1. Check backend terminal for errors
2. Verify backend is running on http://localhost:8000
3. Check CORS errors in browser console

### Problem: "Module not found: bcrypt"
**Solution:**
```bash
pip install bcrypt PyJWT pydantic[email]
```
Then restart backend with Ctrl+C and `python -m uvicorn app:app --reload`

### Problem: Signup form won't submit
**Solution:**
- Ensure all fields are filled
- Check password requirements (6+ chars, 1 uppercase, 1 digit)
- Check passwords match
- Check email format is valid

### Problem: Login says "Invalid email or password" when credentials seem correct
**Solutions:**
1. Clear browser console and try again
2. Check that password is exactly correct (case-sensitive)
3. Verify you signed up with that email (check database)
4. Check backend error logs

### Problem: Session doesn't persist after refresh
**Solution:**
1. Open DevTools → Application → LocalStorage
2. Check for `authToken` and `currentUser` keys
3. If missing, login again and check they appear
4. If they're empty, there's a login issue

### Problem: Can't see 7 training steps on dashboard
**Solution:**
- Check browser resolution isn't too narrow
- Scroll down to see all steps
- Check that dashboard loaded completely

---

## Success Checklist

After completing these 8 steps, you should confirm:

✅ Backend starts without errors  
✅ Frontend starts without errors  
✅ Can signup with new email  
✅ Redirected to dashboard after signup  
✅ Dashboard shows user info and progress  
✅ Can logout successfully  
✅ Can login with same email  
✅ Session persists after page refresh  
✅ Demo account works  
✅ All validation errors display properly  

If all checkboxes are checked: **✅ System is working!**

---

## What's Next?

### Optional: Create Demo Account
If you want the demo account (demo@example.com / Demo123) to actually exist in your database:

1. On login page, click "Sign up"
2. Fill form:
   - Name: Demo User
   - Email: demo@example.com
   - Age: 12
   - Password: Demo123
   - Confirm: Demo123
3. Click "Create Account"
4. You'll be logged in as demo user
5. Go back to login page to see demo credentials work

OR create via API using curl:

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo User",
    "email": "demo@example.com",
    "age": 12,
    "password": "Demo123",
    "password_confirm": "Demo123"
  }'
```

### Upcoming Features

The authentication system is now ready. Next steps include:

1. **Connect training progress to user database**
   - Save step completion status (completed/incomplete)
   - Save assessment results with user_id
   - Display personalized progress on dashboard

2. **Test microphone features with authenticated users**
   - Verify voice recording works with auth tokens
   - Check no auth conflicts with audio processing

3. **Add password reset functionality** (optional)
   - Email-based password reset link
   - Secure token for reset verification

4. **Add user profile/settings page** (optional)
   - Change password
   - Update age
   - View training history

---

## Documentation Files

For more detailed information, see:

- **AUTHENTICATION_IMPLEMENTATION.md** - Full technical documentation
- **AUTHENTICATION_FILES_MODIFIED.md** - Detailed list of all changes
- **AUTHENTICATION_VERIFICATION_CHECKLIST.md** - Comprehensive test scenarios
- **AUTHENTICATION_QUICK_START.md** - Quick reference guide

---

## Support

If you encounter any issues:

1. **Check error messages** in browser console (DevTools F12)
2. **Check backend logs** in terminal where uvicorn is running
3. **Verify dependencies** are installed: `pip list | grep -E "bcrypt|PyJWT|pydantic"`
4. **Restart services**: Stop backend, stop frontend, reinstall deps, restart all
5. **Clear cache**: Close all tabs, clear localStorage, logout, try again

---

## Quick Reference

**Backend:** http://localhost:8000  
**Frontend:** http://localhost:5173  
**Terminal 1:** `cd backend && python -m uvicorn app:app --reload`  
**Terminal 2:** `cd frontend && npm run dev`  

**Demo Account:**  
- Email: demo@example.com
- Password: Demo123

**Endpoints (for testing with curl/Postman):**
- POST /auth/signup
- POST /auth/login  
- GET /auth/me (with Authorization: Bearer &lt;token&gt;)

---

**You're all set! Happy testing! 🚀**
