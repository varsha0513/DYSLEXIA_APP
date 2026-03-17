# Quick Reference Card - Authentication System

Print or bookmark this page for instant access to key information.

---

## 🚀 Installation (Copy-Paste)

```bash
# Install dependencies
pip install bcrypt PyJWT pydantic[email]

# Terminal 1: Backend
cd backend
python -m uvicorn app:app --reload

# Terminal 2: Frontend  
cd frontend
npm run dev
```

---

## 📍 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Demo Email | demo@example.com |
| Demo Password | Demo123 |

---

## 🔑 Demo Account

```
Email:    demo@example.com
Password: Demo123
```

---

## 🔐 Password Requirements

✅ **Valid:**
- TestPass123
- MySecure456
- S7cu77Pass

❌ **Invalid:**
- testpass123 (no uppercase)
- TestPass (no number)
- Test1 (too short)

Template: **[Uppercase][lowercase][Number][6+ chars]**

---

## 📊 Files Created (15 Total)

### Backend
- auth_utils.py ⭐ NEW
- models.py (modified)
- schemas.py (modified)
- app.py (modified)
- crud.py (modified)

### Frontend
- authAPI.ts ⭐ NEW
- AuthContext.tsx ⭐ NEW
- LoginPage.tsx ⭐ NEW
- SignUpPage.tsx ⭐ NEW
- Dashboard.tsx ⭐ NEW
- AuthPages.css ⭐ NEW
- Dashboard.css ⭐ NEW
- App.tsx (modified)
- Navigation.tsx (modified)
- App.css (modified)

---

## 🔗 API Endpoints

### POST /auth/signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 12,
    "password": "TestPass123",
    "password_confirm": "TestPass123"
  }'
```

### POST /auth/login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "TestPass123"
  }'
```

### GET /auth/me
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📚 Documentation

| Document | Time | Purpose |
|----------|------|---------|
| [Getting Started](GETTING_STARTED_AUTHENTICATION.md) | 15 min | Step-by-step setup |
| [Quick Start](AUTHENTICATION_QUICK_START.md) | 5 min | Fast reference |
| [Implementation](AUTHENTICATION_IMPLEMENTATION.md) | 30 min | Technical details |
| [Files Modified](AUTHENTICATION_FILES_MODIFIED.md) | 20 min | All changes |
| [Verification](AUTHENTICATION_VERIFICATION_CHECKLIST.md) | 45 min | Testing guide |
| [Summary](AUTHENTICATION_SYSTEM_SUMMARY.md) | 10 min | Overview |
| [Index](AUTHENTICATION_DOCUMENTATION_INDEX.md) | 5 min | Navigation |

---

## ✅ Test Checklist (Quick)

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can signup with new email
- [ ] Redirects to dashboard
- [ ] Can logout
- [ ] Can login again
- [ ] Session persists on refresh
- [ ] Password validation works

---

## 🆘 Common Issues

| Error | Solution |
|-------|----------|
| "Module not found: bcrypt" | `pip install bcrypt PyJWT pydantic[email]` |
| "Backend not responding" | Check backend is running on port 8000 |
| "Password too weak" | Password must be 6+ chars, 1 uppercase, 1 digit |
| "Email already registered" | Use different email or login instead |
| "Invalid email or password" | Check credentials, verify user exists |
| "Stay logged in but can't login" | Clear localStorage, try again |

---

## 🔄 User Flow

```
Signup        Login         Session
─────────     ─────         ───────
Email      → Email      → Check token
Password   → Password   → Refresh page ✓
Confirm    → Submit     → Still logged in!
Submit
  ↓ Token
  ↓ localStorage
Dashboard
```

---

## 🏗️ Architecture

```
User Browser
    ↓
React App (AuthContext + localStorage)
    ↓
REST API: /auth/signup, /auth/login, /auth/me
    ↓
FastAPI Backend
    ↓
Password hashing (bcrypt)
    ↓
JWT token generation
    ↓
SQLite Database (password_hash field added)
```

---

## 🔒 Security

- Passwords: bcrypt hashed (10 rounds)
- Tokens: JWT with 30-day expiration
- Storage: localStorage on client
- Validation: client-side + server-side
- Headers: Authorization: Bearer <token>

---

## 💾 Data Stored

### localStorage (Client)
- `authToken` - JWT token
- `currentUser` - User object (JSON)

### Database (Server)
- User.username
- User.email (unique)
- User.age
- User.password_hash (bcrypt)
- User.created_at

---

## 📈 Progress Tracking

Dashboard shows:
- **0/7** - Completed steps count
- **Progress bar** - Visual percentage
- **7 Steps** - All training modules selectable
- **User info** - Account details

---

## 🎯 Dashboard Steps

1. Age Selection
2. Reading Assessment
3. Result Analysis
4. Pronunciation Training
5. Eye Focus Test
6. Phrase Training
7. Reading Speed Training

---

## 🔓 Logout

Button location: **Top-right of Dashboard**

Action: Clears token + user from localStorage → Redirects to login

---

## 🔄 Session Recovery

Automatic!

1. Page refresh
2. Close & reopen browser
3. AuthContext checks localStorage
4. Validates token with server
5. Restores session if valid

---

## ⚙️ Configuration

### Backend (auth_utils.py)
- `SECRET_KEY` - From environment or default
- `ALGORITHM` - HS256 (JWT)
- `ACCESS_TOKEN_EXPIRE_DAYS` - 30 (configurable)
- `SALT_ROUNDS` - 10 (bcrypt)

### Frontend (authAPI.ts)
- `API_BASE_URL` - http://localhost:8000
- Storage keys: `authToken`, `currentUser`

---

## 🎓 Key Technologies

| Technology | Use | Version |
|-----------|-----|---------|
| bcrypt | Password hashing | 4.x |
| PyJWT | Token generation | 2.x |
| FastAPI | Backend framework | Latest |
| React | Frontend framework | Latest |
| TypeScript | Type safety | Latest |
| SQLite | Database | Built-in |

---

## 📱 Mobile Responsive

All pages responsive at:
- 📱 Mobile: < 480px
- 📱 Tablet: 480px - 768px
- 💻 Desktop: > 768px

---

## 🎉 Success Indicators

✅ System working when:
- Can signup → login → dashboard
- Session persists on refresh
- All validation works
- No console errors
- No CORS errors

---

## 📋 Next Steps

1. Install dependencies
2. Start backend & frontend
3. Follow [Getting Started](GETTING_STARTED_AUTHENTICATION.md)
4. Complete 8 test scenarios
5. Verify with checklist
6. Ready for production?

---

## 📞 Support

### Check These First
1. Browser console (F12)
2. Backend terminal logs
3. Documentation files above
4. [Quick Start](AUTHENTICATION_QUICK_START.md)

### If Still Stuck
1. Clear browser cache
2. Reinstall dependencies
3. Restart both services
4. Check all 3 python packages installed

---

## 🚀 Deploy Checklist

- [ ] Dependencies installed
- [ ] Backend working
- [ ] Frontend working
- [ ] All tests passing
- [ ] No console errors
- [ ] Session persistence working
- [ ] Password validation working
- [ ] Database has user table with password_hash
- [ ] CORS configured correctly
- [ ] JWT secret key set in environment

---

## 📝 Environment Variables

Backend (.env file)
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./dyslexia.db
```

Frontend (hardcoded for local testing)
```
API_BASE_URL=http://localhost:8000
```

---

## 🔐 Password Hashing Flow

```
Plain: "TestPass123"
         ↓
    bcrypt hash
    (10 rounds)
         ↓
hashed: "$2b$10$Yh...xyz"
         ↓
    stored in DB
    (never plain text)
```

---

## 🎫 JWT Token Flow

```
User login + password
    ↓
Verify password hash
    ↓
Create JWT payload
    {
      "sub": user_id,
      "exp": future_timestamp,
      "iat": now
    }
    ↓
Sign with SECRET_KEY
    ↓
Return token to client
    "eyJ0eXAiOiJKV1QiLCJhbGc..."
    ↓
Client stores in localStorage
    ↓
Send in Authorization header
    on future API calls
```

---

## 🎯 One-Minute Test

1. Signup: **test@example.com** / **TestPass123**
2. ✓ See dashboard
3. Logout
4. Login: **test@example.com** / **TestPass123**
5. ✓ See dashboard again
6. Refresh page
7. ✓ Still logged in

If all 7 checks pass → **System working! ✅**

---

**Last Updated:** January 2024  
**Status:** Ready for Production  
**Version:** 1.0
