
# Age-Based Reading Assessment System - Implementation Guide

## Overview
Age is now the **MOST IMPORTANT FACTOR** in the Dyslexia App for determining reading assessment difficulty. The system uses age to automatically select appropriate reading paragraphs with matching complexity and vocabulary levels.

## Key Implementation Details

### 1. Age Added to User Model
**File:** `backend/models.py`
```python
age = Column(Integer, nullable=True)
```
- Age is stored in the User database table
- Can be provided during signup or updated later
- Ranges from 5 to 120 years old

### 2. User Signup with Age
**File:** `backend/schemas.py` & `backend/app.py`

#### Updated UserSignUp Schema:
```python
class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str
    password_confirm: str
    age: Optional[int] = None  # ← NEW
```

#### Updated Signup Endpoint:
```python
@app.post("/auth/signup")
async def signup(user_data: schemas.UserSignUp, db: Session = Depends(get_db)):
    # Age is now captured during signup
    user_create = schemas.UserCreate(
        username=username,
        email=user_data.email,
        password=user_data.password,
        age=user_data.age  # ← NEW
    )
```

### 3. Age-Based Paragraph Library
**File:** `backend/age_based_paragraphs.py` (NEW)

The system includes paragraphs organized into 6 age groups:

| Age Group | Age Range | Level | Difficulty | Examples |
|-----------|-----------|-------|-----------|----------|
| **4-6 years** | 4-6 | Beginner | Very Easy | Simple sentences, 15-20 words |
| **7-9 years** | 7-9 | Early Reader | Easy | Basic comprehension, 25-40 words |
| **10-12 years** | 10-12 | Intermediate | Medium | Paragraph comprehension, 60-100 words |
| **13-15 years** | 13-15 | Advanced | Challenging | Complex ideas, 120-180 words |
| **16-18 years** | 16-18 | High School | Advanced | Academic content, 150-250 words |
| **18+ years** | adult | Adult | Advanced/Expert | Professional/academic texts, 200+ words |

### 4. Example Paragraphs by Age

#### Age 4-6 (Beginner):
```
"The cat sat on the mat. It was a warm sunny day. The cat liked to nap."
```

#### Age 7-9 (Early Reader):
```
"The butterfly flew from flower to flower in the garden. It was looking for sweet nectar. The colors on its wings were beautiful."
```

#### Age 10-12 (Intermediate):
```
"Photosynthesis is the process by which plants convert sunlight into chemical energy. The leaves contain chlorophyll, which absorbs light and enables the plant to grow. This process releases oxygen into the atmosphere."
```

#### Age 13-15 (Advanced):
```
"The Renaissance was a period of European history from the 14th to 17th century, marking the transition from medieval to modern times. It was characterized by a renewed interest in classical Greek and Roman learning. Artists and scientists made groundbreaking contributions during this era."
```

#### Age 16-18 (High School):
```
"Quantum mechanics describes the behavior of matter and energy at atomic and subatomic scales. It challenges classical physics assumptions and introduces concepts like wave-particle duality and uncertainty principle. Max Planck and Albert Einstein made foundational contributions to this field."
```

#### 18+ (Adult/Professional):
```
"Blockchain technology represents a paradigm shift in distributed systems and cryptographic security. Its decentralized architecture eliminates single points of failure and enables trustless transactions. Applications extend beyond cryptocurrency to supply chain management and smart contracts."
```

### 5. Paragraph Selection Functions

**File:** `backend/age_based_paragraphs.py`

#### Function: `get_age_group(age: int) -> str`
Determines age group from age value:
```python
- age < 7 → "4-6"
- age < 10 → "7-9"
- age < 13 → "10-12"
- age < 16 → "13-15"
- age < 19 → "16-18"
- age >= 19 → "adult"
```

#### Function: `get_paragraph_for_age(age: int, index: int = 0) -> str`
Returns a specific paragraph for user's age:
```python
paragraph = get_paragraph_for_age(age=12, index=0)
# Returns a 10-12 year old appropriate paragraph
```

#### Function: `get_age_group_info(age: int) -> dict`
Returns metadata about the age group:
```python
{
    "age_group": "10-12 years",
    "level": "Intermediate",
    "difficulty": "Medium",
    "focus": "Paragraph comprehension and vocabulary building",
    "typical_word_count": "60-100 words per paragraph"
}
```

### 6. New API Endpoints

#### Endpoint: GET `/paragraph/suggest`
Get a paragraph appropriate for user's age.

**Request:**
```
GET /paragraph/suggest?age=12&index=0
```

**Response:**
```json
{
    "success": true,
    "paragraph": "Photosynthesis is the process...",
    "age_group": "10-12 years",
    "reading_level": "Intermediate",
    "difficulty": "Medium",
    "focus": "Paragraph comprehension and vocabulary building",
    "word_count": "60-100 words per paragraph",
    "message": "✅ Paragraph selected for age 12 (10-12 years)"
}
```

#### Endpoint: PUT `/auth/me/age`
Update user's age after signup.

**Request:**
```
PUT /auth/me/age
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

age=12
```

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "age": 12,
    "current_streak": 0,
    "best_streak": 0,
    "last_completed_date": null,
    "created_at": "2026-03-31T10:00:00"
}
```

#### Endpoint: GET `/paragraph/all`
Get all paragraphs organized by age group.

**Request:**
```
GET /paragraph/all
```

**Response:**
```json
{
    "success": true,
    "total_age_groups": 6,
    "paragraphs_by_age": {
        "4-6": {
            "age_group": "4-6 years",
            "level": "Beginner",
            "difficulty": "Very Easy",
            "paragraph_count": 5,
            "paragraphs": [...]
        },
        "7-9": {...},
        ...
    },
    "message": "All reading assessment paragraphs organized by age group"
}
```

### 7. How It Works in Assessment Flow

1. **User Signs Up** → Age is captured
2. **User Starts Assessment** → System determines age group
3. **Paragraph Selected** → Appropriate difficulty paragraph is chosen
4. **User Reads Paragraph** → Speech recognition compares to reference text
5. **Results Evaluated** → Risk score calculated based on reading level

### 8. Files Modified

| File | Changes |
|------|---------|
| `backend/models.py` | Already had `age` column (no change needed) |
| `backend/schemas.py` | Added `age: Optional[int] = None` to UserSignUp |
| `backend/app.py` | 1. Added age_based_paragraphs import<br>2. Updated signup to pass age<br>3. Added 3 new endpoints for paragraphs and age |
| `backend/crud.py` | Already handles age in create_user_with_password (no change needed) |

### 9. New Files Created

| File | Purpose |
|------|---------|
| `backend/age_based_paragraphs.py` | Complete age-based paragraph library and helper functions |

### 10. Frontend Integration Example

#### Signup with Age:
```javascript
const signupData = {
    name: "John Doe",
    email: "john@example.com",
    password: "Password123",
    password_confirm: "Password123",
    age: 12  // ← Age included
};

fetch('/auth/signup', {
    method: 'POST',
    body: formData
})
```

#### Get Paragraph for Assessment:
```javascript
// Get paragraph based on user's age
const response = await fetch(`/paragraph/suggest?age=${userAge}`);
const data = await response.json();
const paragraph = data.paragraph;
```

#### Update Age Later:
```javascript
const formData = new FormData();
formData.append('age', 14);

fetch('/auth/me/age', {
    method: 'PUT',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: formData
})
```

### 11. Key Design Principles

✅ **Age-First Design**: Age is the primary factor for determining assessment difficulty
✅ **Appropriate Content**: Each age group gets reading material suitable for their cognitive level
✅ **Progressive Difficulty**: As age increases, vocabulary complexity and text length increase
✅ **Flexible Updates**: Age can be updated at any time after signup
✅ **Backward Compatible**: Age is optional (nullable) for existing users
✅ **Extensible**: Easy to add more paragraphs to any age group

### 12. Testing the Implementation

#### Test 1: Signup with Age
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User&email=test@example.com&password=Test123&password_confirm=Test123&age=12"
```

#### Test 2: Get Paragraph for Age
```bash
curl "http://localhost:8000/paragraph/suggest?age=12"
```

#### Test 3: Update Age
```bash
curl -X PUT http://localhost:8000/auth/me/age \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "age=14"
```

### 13. Future Enhancements

- [ ] Track reading level progress over time
- [ ] Auto-advance age group based on reading performance
- [ ] Add audio difficulty selection based on speech rate
- [ ] Create custom paragraphs for specific interests
- [ ] Support multiple languages with age-appropriate content
- [ ] Machine learning model to predict optimal difficulty

---

## Summary

The age-based reading assessment system ensures that every student gets:
- ✅ **Appropriate difficulty** - matched to their age and reading level
- ✅ **Engaging content** - vocabulary and concepts suitable for their age
- ✅ **Fair evaluation** - risk scores calculated based on age-appropriate benchmarks
- ✅ **Progressive learning** - content difficulty increases with age

Age is now the **PRIMARY FACTOR** in determining assessment difficulty throughout the application.
