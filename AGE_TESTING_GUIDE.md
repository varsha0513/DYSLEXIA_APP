
# Age-Based System - Testing & Verification Guide

**Status**: ✅ READY FOR TESTING
**Date**: March 31, 2026

---

## 🎯 What Was Fixed

### Problem:
- Age was not being asked during signup
- Defaulted to age 5 (hardcoded)
- User couldn't enter their age
- Progress not personalized by age

### Solution:
- ✅ Added age field to signup form
- ✅ Age is now REQUIRED (5-120)
- ✅ Age stored with user profile
- ✅ Age used for assessment paragraphs
- ✅ Progress tracked by age

---

## 🧪 Testing Steps

### Part 1: Frontend Age Field

**1. Start the application**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**2. Visit signup page**
- Open http://localhost:5173
- You should see signup form

**3. Check for Age Field** ✅
- Look for "Age" label below "Confirm Password"
- Should show input field with:
  - Type: number
  - Placeholder: "Enter your age (5-120)"
  - Min: 5
  - Max: 120

---

### Part 2: Age Validation

**Test Valid Age**:
```
Name: John Doe
Email: john@test.com
Password: Test123
Confirm: Test123
Age: 12  ← Valid (between 5-120)
```
Result: ✅ Should successfully create account

**Test Too Young**:
```
Age: 4  ← Invalid (less than 5)
```
Result: ✅ Should show error: "Age must be between 5 and 120"

**Test Too Old**:
```
Age: 150  ← Invalid (greater than 120)
```
Result: ✅ Should show error: "Age must be between 5 and 120"

**Test Missing Age**:
```
Age: [empty]  ← Invalid (required)
```
Result: ✅ Should show error: "Age is required"

---

### Part 3: Account Creation with Age

**1. Fill signup form completely**:
```
Full Name: Jane Smith
Email: jane.smith@test.com
Password: SecurePass123
Confirm Password: SecurePass123
Age: 14
```

**2. Click "Create Account"**
- Should see: "⏳ Creating Account..." (loading)
- Then: "✅ Redirected to Dashboard"

**3. Verify Age Was Saved**:
- Open browser DevTools (F12)
- Go to Storage → localStorage
- Look for entry with "user" key
- Should show: `"age": 14`

---

### Part 4: Email as Unique Identifier

**Test 1: Same email cannot be used twice**
```
1st signup: jane@example.com, age 10
2nd signup: jane@example.com, age 15
```
Result: ✅ 2nd signup should fail with "Email already registered"

**Test 2: Different emails are separate users**
```
User 1: jane@example.com, age 10
User 2: john@example.com, age 15
```
Result: ✅ Both accounts created, each with their own age

---

### Part 5: Age-Based Paragraph Selection

**Scenario: User starts assessment**

1. **User with age 10**:
   - Age group: "10-12 years"
   - Difficulty: "Medium"
   - Paragraph: Science topic, 60-100 words

2. **User with age 7**:
   - Age group: "7-9 years"
   - Difficulty: "Easy"
   - Paragraph: Story, 25-40 words

3. **User with age 16**:
   - Age group: "16-18 years"
   - Difficulty: "Advanced"
   - Paragraph: Academic, 150-250 words

---

## 📋 Files Modified Checklist

### Frontend Files Updated:
- [x] `frontend/src/components/SignUpPage.tsx`
  - Added age to formData state
  - Added age input field to form
  - Added age validation
  - Updated handleSubmit to pass age

- [x] `frontend/src/contexts/AuthContext.tsx`
  - Updated signup function signature to accept age
  - Updated signup call to pass age to API

- [x] `frontend/src/utils/authAPI.ts`
  - Added `age?: number` to SignUpData interface
  - Age included in signup request

- [x] `frontend/src/components/AuthPages.css`
  - Added `.age-hint` styling for helper text

### Backend Verification:
- ✅ `backend/schemas.py` - UserSignUp has age field
- ✅ `backend/app.py` - Signup endpoint captures age
- ✅ `backend/models.py` - User model has age column
- ✅ `backend/crud.py` - CRUD methods handle age

---

## 🔗 API Call Verification

### What gets sent to backend now:

**Before**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "Password123",
  "password_confirm": "Password123"
}
```

**Now** ✅:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "Password123",
  "password_confirm": "Password123",
  "age": 12
}
```

### What gets returned from backend:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "age": 12,
    "current_streak": 0,
    "best_streak": 0,
    "last_completed_date": null,
    "created_at": "2026-03-31T10:00:00"
  }
}
```

Notice: `"age": 12` is returned! ✅

---

## 🧬 Data Flow Verification

### Test Complete Flow:

**Step 1**: Browse to http://localhost:5173
**Result**: Signup form loads

**Step 2**: Fill all fields including age (e.g., age=14)
**Result**: Form shows all fields validated

**Step 3**: Submit form
**Network Monitor** (F12 → Network):
```
POST /auth/signup
Request body includes:
{
  "name": "...",
  "email": "...",
  "password": "...",
  "password_confirm": "...",
  "age": 14
}

Response includes:
{
  "user": {
    "age": 14,
    ...
  }
}
```

**Step 4**: After signup (in localStorage)
**F12 → Application → localStorage**:
```
Key: "user"
Value: {
  "id": 1,
  "age": 14,
  "email": "...",
  ...
}
```

**Step 5**: Start assessment
**System behavior**:
- Gets user.age from localStorage (14)
- Determines age group: "13-15"
- Selects appropriate paragraph
- Shows to user

---

## ✅ Success Criteria

| Test | Expected Result | Status |
|------|-----------------|--------|
| Age field visible | ✅ Shows in form | 🔄 Test |
| Age required | ✅ Error if empty | 🔄 Test |
| Age range 5-120 | ✅ Validates correctly | 🔄 Test |
| Age sent to backend | ✅ In request body | 🔄 Test |
| Age stored in DB | ✅ User record has age | 🔄 Test |
| Age returned from API | ✅ In response object | 🔄 Test |
| Age in localStorage | ✅ Persisted client-side | 🔄 Test |
| Age unique per email | ✅ Jane@ex.com → age 10 | 🔄 Test |
| Age used for paragraphs | ✅ Affects content selection | 🔄 Test |
| Progress by age | ✅ Tracked per age group | 🔄 Test |

---

## 🐛 Debugging

### If age field is not showing:
```bash
# Clear browser cache
Ctrl+Shift+Delete (Windows)
Cmd+Shift+Delete (Mac)

# Or do hard refresh
Ctrl+Shift+R (Windows)
Cmd+Shift+R (Mac)
```

### If age validation fails:
```
Check browser console (F12 → Console)
Look for validation error messages
Verify age is number and 5-120
```

### If backend rejects age:
```
Check backend is running: python app.py
Check backend terminal for error messages
Verify age is being sent in request body
```

### To see all API requests:
```
Open DevTools: F12
Go to Network tab
Do signup process
Click on /auth/signup request
Check:
- Request body (should have age)
- Response body (should return age)
```

---

## 🎓 Age Group Examples

Once working, test with different ages:

| Age | Entry | Expected Paragraph |
|-----|-------|-------------------|
| 6 | "The cat sat..." | Very Easy |
| 8 | "The butterfly flew..." | Easy |
| 11 | "Photosynthesis is..." | Medium |
| 14 | "The Renaissance was..." | Challenging |
| 17 | "Quantum mechanics..." | Advanced |
| 25 | "Blockchain technology..." | Expert |

---

## 📊 Testing Spreadsheet

Copy and use this to track your tests:

```
Test Case | Input Age | Expected | Result | Pass?
----------|-----------|----------|--------|------
Valid age | 12 | Account created | _____ | [ ]
Too young | 4 | Error shown | _____ | [ ]
Too old | 150 | Error shown | _____ | [ ]
Missing | (empty) | Error shown | _____ | [ ]
Email unique | jane_1 & jane_2 | Both different | _____ | [ ]
Stored | age 12 | In localStorage | _____ | [ ]
Assessment | age 12 | Medium paragraph | _____ | [ ]
Different user | age 8 | Easy paragraph | _____ | [ ]
```

---

## 🚀 Complete Test Scenario

### A Complete Test from Start to Finish:

```
1. Start backend:
   cd backend && python app.py
   ✓ Backend running on :8000

2. Start frontend:
   cd frontend && npm run dev
   ✓ Frontend running on :5173

3. Go to signup page:
   http://localhost:5173
   ✓ Signup form visible

4. Fill form:
   - Name: Test User
   - Email: testuser@dyslexia.test
   - Password: TestPass123
   - Confirm: TestPass123
   - Age: 12 ← VERIFY THIS FIELD EXISTS
   ✓ All fields filled

5. Submit:
   Click "Create Account"
   ✓ Account creating...
   ✓ Redirected to dashboard

6. Verify in console (F12):
   Storage → localStorage
   Look for user key
   Check: "age": 12
   ✓ Age stored in localStorage

7. Start Assessment:
   Click on reading assessment
   ✓ Paragraph appears
   Verify: Should be "Medium" difficulty
   (For age 12, should be 10-12 group)
   ✓ Age-appropriate content shown

8. Verify Backend Database:
   SQLite query: SELECT * FROM users WHERE email='testuser@dyslexia.test'
   Check age column = 12
   ✓ Age persisted in database

SUCCESS! ✅ Age system is working end-to-end
```

---

## 📞 Troubleshooting

### Error: "Age field not appearing"
- **Cause**: Stale JavaScript
- **Solution**: Clear cache and hard refresh (Ctrl+Shift+R)

### Error: "Age validation error"
- **Cause**: Age outside 5-120 range
- **Solution**: Enter valid age (e.g., 12)

### Error: "Signup fails even with age"
- **Cause**: Backend not accepting age
- **Solution**: Check backend is running, check error message

### Error: "Age not in localStorage"
- **Cause**: Signup didn't complete properly
- **Solution**: Check network tab for failed requests

---

## ✨ Next Steps After Verification

1. ✅ Verify age field appears in signup
2. ✅ Verify age validation works
3. ✅ Verify account created with age
4. ✅ Verify age stored and retrieved
5. ✅ Verify age used for paragraph selection
6. 🔄 Test with different ages (5, 8, 12, 15, 18, 25)
7. 🔄 Test unique email constraint (same email can't be used twice)
8. 🔄 Verify progress tracked per user (by email identifier)

---

## 🎉 Success Message

When everything works:
- ✅ Users enter age during signup
- ✅ Age stored with their email (unique identifier)
- ✅ Age remembered across sessions
- ✅ Age determines reading difficulty
- ✅ Students get age-appropriate assessments!

---

**Ready to test?** Start with the application and follow the testing steps above! 🚀

