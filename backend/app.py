"""
FastAPI Backend API for Dyslexia Assessment System
Wraps the complete reading assessment pipeline into REST endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import io
import wave
import json
import os
import time
from vosk import Model, KaldiRecognizer
from text_comparison import compare_text, get_performance_feedback
from reading_speed import ReadingSpeedAnalyzer
from dyslexia_risk_scoring import DyslexiaRiskScorer
from text_to_speech import DyslexiaAssistanceEngine
from pronunciation_trainer import PronunciationTrainer, PronunciationComparator
from speed_trainer import SpeedTrainer
from phrase_trainer import PhraseTrainer
from database import init_db, get_db, engine
from auth_utils import hash_password, verify_password, create_access_token, decode_access_token, validate_email, validate_password
from crud import (
    UserCRUD,
    AssessmentCRUD,
    ResultCRUD,
    PronunciationCRUD,
    ProgressCRUD,
    SpeedTrainerCRUD,
    ChunkReadingCRUD
)
import models
import schemas

# Initialize FastAPI
app = FastAPI(
    title="Dyslexia Assessment API",
    description="Comprehensive dyslexia risk assessment through reading",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database when app starts"""
    init_db()
    print("[OK] Database tables initialized")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Vosk model
model_path = "../model/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    raise RuntimeError(
        f"[ERROR] Vosk model not found at {model_path}. "
        f"Please download it first."
    )

model = Model(model_path)

# Initialize TTS Engine for Assistance Module
try:
    tts_engine = DyslexiaAssistanceEngine(rate=100, volume=0.9)
    print("[OK] Assistance Module (TTS) ready")
except Exception as e:
    print(f"[WARN] TTS Engine initialization warning: {e}")
    tts_engine = None

# Initialize Pronunciation Trainer
try:
    pronunciation_trainer = PronunciationTrainer(
        vosk_model=model,
        tts_engine=tts_engine
    )
    print("[OK] Pronunciation Trainer ready")
except Exception as e:
    print(f"[WARN] Pronunciation Trainer initialization warning: {e}")
    pronunciation_trainer = None

# Initialize Speed Trainer Sessions storage
# Speed trainer session storage
speed_trainer_sessions = {}

# Initialize Phrase Trainer Sessions storage
# Phrase trainer session storage
phrase_trainer_sessions = {}


# ================== Pydantic Models ==================

class AssessmentRequest(BaseModel):
    """Request model for reading assessment"""
    age: int
    paragraph: str

    class Config:
        json_schema_extra = {
            "example": {
                "age": 10,
                "paragraph": "The quick brown fox jumps over the lazy dog."
            }
        }


class PronunciationCheckResult(BaseModel):
    """Result of pronunciation check"""
    word: str
    recognized: str
    correct: str
    is_correct: bool
    similarity_ratio: float
    feedback: str
    pronunciation_audio: Optional[str] = None
    raw_recognized: str = ""
    exact_match: bool = False


class PronunciationFeedback(BaseModel):
    """Feedback for pronunciation attempt"""
    word: str
    attempt_number: int
    is_correct: bool
    similarity_ratio: float
    feedback: str
    should_retry: bool
    pronunciation_audio: Optional[str] = None


class TrainingSessionResult(BaseModel):
    """Result of a complete training session"""
    word: str
    success: bool
    total_attempts: int
    final_status: str
    summary: dict


class SpeedMetrics(BaseModel):
    """Speed metrics from reading assessment"""
    elapsed_time_seconds: float
    elapsed_time_formatted: str
    spoken_words: int
    wpm: float
    speed_category: str
    speed_indicator: str
    dyslexia_risk: str


class AccuracyMetrics(BaseModel):
    """Accuracy metrics from reading assessment"""
    total_words: int
    correct_words: int
    wrong_words: int
    missing_words: int
    extra_words: int
    accuracy_percent: float


class RiskAssessment(BaseModel):
    """Dyslexia risk assessment results"""
    risk_score: float
    risk_level: str
    component_scores: dict
    indicators: list
    recommendations: list
    summary: str


class WordError(BaseModel):
    """Individual word error with correction"""
    spoken: str
    correct: str


class AssistanceData(BaseModel):
    """Assistance module data for helping users"""
    has_errors: bool
    error_count: int
    wrong_words: list  # List of (spoken, correct) tuples
    missing_words: list  # List of missing words
    extra_words: list  # List of extra words
    assistance_enabled: bool


class AssessmentResponse(BaseModel):
    """Complete assessment response"""
    reference_text: str
    recognized_text: str
    age: int
    speed_metrics: SpeedMetrics
    accuracy_metrics: AccuracyMetrics
    accuracy_feedback: str
    difficulty_assessment: str
    risk_assessment: RiskAssessment
    assistance: Optional[AssistanceData] = None
    status: str = "success"


class SpeedTrainerRound(BaseModel):
    """Configuration for a single training round"""
    round_number: int
    wpm: int
    interval_ms: int
    duration_seconds: float
    status: str = "pending"


class SpeedTrainerSession(BaseModel):
    """Speed trainer session data"""
    text: str
    words: List[str]
    total_words: int
    current_round: int
    current_word_index: int
    current_word: Optional[str]
    is_paused: bool
    is_completed: bool
    rounds: List[SpeedTrainerRound]
    session_id: str = ""


class PaceReadingRequest(BaseModel):
    """Request to prepare pace reading training"""
    text: str
    speeds: Optional[List[int]] = None  # Custom WPM values

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog",
                "speeds": [60, 75, 90]
            }
        }


class PaceReadingResponse(BaseModel):
    """Response from pace reading preparation"""
    text: str
    words: List[str]
    total_words: int
    speeds: List[int]
    intervals: List[int]
    session_id: str = ""


class SpeedTrainerAction(BaseModel):
    """Action on a speed trainer session"""
    action: str  # start, pause, resume, reset, advance_word
    session_id: Optional[str] = None


class SpeedTrainerStats(BaseModel):
    """Statistics from a speed training session"""
    total_words: int
    total_rounds: int
    completed_rounds: int
    current_round: int
    total_duration_seconds: float
    average_wpm: float
    min_wpm: int
    max_wpm: int
    is_completed: bool


class SpeedTrainerResults(BaseModel):
    """Results submission from speed trainer session"""
    session_id: str
    elapsed_time_seconds: float


class SpeedTrainerCompletionResult(BaseModel):
    """Completion result with calculated WPM"""
    session_id: str
    total_words: int
    elapsed_time_seconds: float
    calculated_wpm: float
    status: str = "completed"
    message: str = ""


# ================== Chunk Reading (Phrase Training) Models ==================

class ChunkReadingRequest(BaseModel):
    """Request to prepare chunk reading training"""
    text: str
    min_phrase_length: Optional[int] = 2
    max_phrase_length: Optional[int] = 4

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog",
                "min_phrase_length": 2,
                "max_phrase_length": 4
            }
        }


class ChunkReadingResponse(BaseModel):
    """Response from chunk reading preparation"""
    text: str
    phrases: List[str]
    total_phrases: int
    min_phrase_length: int
    max_phrase_length: int
    session_id: str = ""


class ChunkReadingSession(BaseModel):
    """Chunk reading session data"""
    text: str
    phrases: List[str]
    total_phrases: int
    current_phrase_index: int
    current_phrase: Optional[str]
    is_paused: bool
    is_completed: bool
    session_id: str = ""


class ChunkReadingAction(BaseModel):
    """Action on a chunk reading session"""
    action: str  # start, pause, resume, reset, advance_phrase
    session_id: Optional[str] = None


class ChunkReadingStats(BaseModel):
    """Statistics from a chunk reading session"""
    total_phrases: int
    current_phrase_index: int
    phrases_completed: int
    progress_percent: float
    is_completed: bool


class ChunkReadingResults(BaseModel):
    """Results submission from chunk reading session"""
    session_id: str
    elapsed_time_seconds: float


class ChunkReadingCompletionResult(BaseModel):
    """Completion result with reading metrics"""
    session_id: str
    total_phrases: int
    total_words: int
    elapsed_time_seconds: float
    calculated_wpm: float
    phrases_per_second: float
    status: str = "completed"
    message: str = ""


# ================== Helper Functions ==================

def process_audio_file(audio_bytes: bytes, filename: str = 'audio.wav') -> str:
    """
    Process audio file and extract recognized text using Vosk
    Expects WAV format audio

    Args:
        audio_bytes: Raw WAV audio data
        filename: Original filename (for logging)

    Returns:
        Recognized text from the audio
    """
    try:
        print(f"[AUDIO] Processing audio file: {filename}")
        print(f"[AUDIO] Total audio bytes received: {len(audio_bytes)}")

        # Validate audio has content
        if len(audio_bytes) < 100:
            print(f"[ERROR] Audio file too small: {len(audio_bytes)} bytes")
            return ""

        # Read WAV file
        audio_stream = io.BytesIO(audio_bytes)
        with wave.open(audio_stream, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()

            print("[AUDIO] WAV Properties:")
            print(f"   - Channels: {channels}")
            print(f"   - Sample Width: {sample_width} bytes (16-bit = 2)")
            print(f"   - Sample Rate: {sample_rate} Hz")
            print(f"   - Frames: {num_frames}")
            print(f"   - Duration: {num_frames / sample_rate:.2f} seconds")

            # Validate audio format
            if channels != 1:
                print(
                    f"[WARN] Converting {channels} channels to mono..."
                )
            if sample_width != 2:
                msg = f"Expected 16-bit audio, got {sample_width*8}-bit"
                print(f"[WARN] {msg}")

            # Check if audio has actual sound (rough estimate)
            audio_data = wav_file.readframes(num_frames)
            if len(audio_data) < 100:
                msg = f"[ERROR] Audio data is too small: {len(audio_data)}"
                print(msg + " bytes")
                print("   [ERROR] Audio is likely silent or corrupted")
                return ""

            # Reset stream for recognition
            audio_stream.seek(0)

            # Create recognizer - Vosk model expects 16kHz mono
            if sample_rate != 16000:
                msg = f"Vosk needs 16000 Hz, audio is {sample_rate} Hz"
                print(f"[WARN] {msg}")

            print("[VOSK] Creating Vosk recognizer (target 16kHz)...")
            recognizer = KaldiRecognizer(model, sample_rate)
            recognizer.SetWords(None)  # Use default word list

            # Process audio in optimal chunk size for Vosk
            frames_processed = 0
            chunks_with_results = 0
            interim_results = []

            print("[VOSK] Feeding audio to Vosk recognizer...")
            with wave.open(audio_stream, 'rb') as wav_file:
                while True:
                    # Better recognition (4096 bytes chunk)
                    data = wav_file.readframes(4096)
                    if len(data) == 0:
                        break

                    # Feed data to recognizer
                    try:
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            if result.get("text"):
                                interim_results.append(
                                    result.get("text")
                                )
                                chunks_with_results += 1
                                txt = result.get('text')
                                print(
                                    f"[OK] Interim result "
                                    f"#{chunks_with_results}: {txt}"
                                )
                    except Exception as e:
                        print(f"[WARN] Error processing chunk: {e}")

                    frames_processed += 1
                    if frames_processed % 5 == 0:
                        msg = f"[AUDIO] Processed {frames_processed} "
                        print(msg + "chunks...")

            # Get final result
            try:
                final_result = json.loads(recognizer.FinalResult())
                final_text = final_result.get("text", "")
            except Exception as e:
                print(f"[WARN] Error getting final result: {e}")
                final_text = ""

            print("[VOSK] VOSK RECOGNITION RESULTS:")
            print(f"   - Total chunks processed: {frames_processed}")
            print(f"   - Chunks with results: {chunks_with_results}")
            print(f"   - Interim results collected: {len(interim_results)}")
            if interim_results:
                print(f"   - Interim text: {' '.join(interim_results)}")
            print(f"   - Final recognized text: {final_text}")

            # Combine interim and final results if we got something
            combined_text = final_text
            if not final_text and interim_results:
                combined_text = ' '.join(interim_results)

            if not combined_text:
                print("\n[ERROR] NO SPEECH RECOGNIZED")
                print("   Possible causes:")
                msg1 = "1. ⚠️  Audio is truly silent"
                print(f"   {msg1} (check microphone volume)")
                msg2 = "2. ⚠️  Audio format is corrupted"
                print(f"   {msg2} (resampling failed?)")
                msg3 = "3. ⚠️  Speech in different language"
                print(f"   {msg3}/heavy accent")
                msg4 = "4. ⚠️  Audio envelope is wrong"
                print(f"   {msg4} (too soft to detect)")

            return combined_text.strip()

    except wave.Error as e:
        print(f"❌ Failed to read audio as WAV: {e}")
        print("   This usually means the WAV encoding is broken")
        raise ValueError(f"Invalid WAV audio format: {e}")
    except Exception as e:
        print(f"❌ Audio processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to process audio: {str(e)}")


# ================== API Endpoints ==================

# ================= Authentication Endpoints =================

@app.post("/auth/signup", response_model=schemas.LoginResponse)
async def signup(user_data: schemas.UserSignUp, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User signup data (name, email, age, password)
        db: Database session
        
    Returns:
        Login response with access token and user data
    """
    try:
        # Validate email format
        if not validate_email(user_data.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check if email already exists
        user_crud = UserCRUD(db)
        existing_user = user_crud.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate password
        if user_data.password != user_data.password_confirm:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        is_valid, message = validate_password(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Hash password for the username too
        username = user_data.name.replace(" ", "_").lower()
        
        # Create user
        user_create = schemas.UserCreate(
            username=username,
            email=user_data.email,
            password=user_data.password,
            age=user_data.age
        )
        
        user = user_crud.create_user_with_password(user_create)
        
        # Create access token
        access_token = create_access_token(data={"user_id": user.id, "email": user.email})
        
        user_response = schemas.UserResponse.from_orm(user)
        
        return schemas.LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")


@app.post("/auth/login", response_model=schemas.LoginResponse)
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login a user with email and password.
    
    Args:
        credentials: Login credentials (email, password)
        db: Database session
        
    Returns:
        Login response with access token and user data
    """
    try:
        # Get user by email
        user_crud = UserCRUD(db)
        user = user_crud.get_by_email(credentials.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token(data={"user_id": user.id, "email": user.email})
        
        user_response = schemas.UserResponse.from_orm(user)
        
        return schemas.LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.
    
    Args:
        authorization: Authorization header with token
        db: Database session
        
    Returns:
        Current user data
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_crud = UserCRUD(db)
        user = user_crud.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return schemas.UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# ================== TTS Endpoints ================

@app.post("/tts/word")
async def generate_word_pronunciation(word: str = Form(...)):
    """
    Generate audio pronunciation for a word

    Args:
        word: Word to pronounce

    Returns:
        WAV audio file of word pronunciation
    """
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")

        if not tts_engine:
            raise HTTPException(
                status_code=503,
                detail="TTS Engine not available"
            )

        print(f"🔊 Generating pronunciation for: '{word}'")
        audio_bytes, _ = tts_engine.generate_audio_file(word)

        if not audio_bytes:
            detail = "Failed to generate audio"
            raise HTTPException(status_code=500, detail=detail)

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={word}.wav"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )


@app.post("/tts/correction")
async def get_word_correction(
    wrong_word: str = Form(...),
    correct_word: str = Form(...)
):
    """
    Get complete word correction assistance (audio + feedback)

    Args:
        wrong_word: Word spoken by user
        correct_word: Correct word to learn

    Returns:
        JSON with audio URL and assistance message
    """
    try:
        if not wrong_word or not correct_word:
            raise HTTPException(status_code=400, detail="Both words required")

        if not tts_engine:
            detail = "TTS Engine not available"
            raise HTTPException(status_code=503, detail=detail)

        print(
            f"🆘 Generating correction: '{wrong_word}' "
            f"-> '{correct_word}'"
        )
        assistance = tts_engine.generate_word_assistance(
            wrong_word, correct_word
        )

        return assistance

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Correction Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Correction generation failed: " + str(e)
        )


@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "name": "Dyslexia Assessment API",
        "version": "1.0.0",
        "status": "🟢 Running",
        "endpoints": {
            "assess_with_audio": (
                "POST /assess - Send paragraph, age, audio file"
            ),
            "assess_with_text": (
                "POST /assess-text - Send paragraph, age, "
                "recognized text (for testing)"
            ),
            "tts_word": (
                "POST /tts/word - Generate audio pronunciation"
            ),
            "tts_correction": (
                "POST /tts/correction - Get word correction "
                "with audio assistance"
            ),
            "health": "GET /health - Health status"
        },
        "features": {
            "speech_recognition": "Vosk-based real-time recognition",
            "accuracy_analysis": "Word-level comparison",
            "speed_analysis": "WPM calculation",
            "dyslexia_risk": "Comprehensive scoring",
            "assistance_module": "TTS-based pronunciation help 🆘"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "🟢 Healthy", "model": "Vosk loaded"}


@app.post("/assess", response_model=AssessmentResponse)
async def assess_reading(
    age: int = Form(...),
    paragraph: str = Form(...),
    audio_file: UploadFile = File(
        ..., description="WAV audio of user reading"
    ),
    recognized_text: str = Form(
        default='',
        description="Optional: Pre-recognized text from frontend"
    ),
    db: Session = Depends(get_db)
):
    """
    Complete reading assessment endpoint

    Processes audio file and compares with reference paragraph to generate:
    - Accuracy metrics (correct/wrong/missing words)
    - Reading speed (WPM)
    - Dyslexia risk scores
    - Detailed feedback

    Args:
        age: User age for context-aware assessment
        paragraph: Reference text the user should read
        audio_file: WAV file containing the user's reading
        recognized_text: Optional pre-recognized text from
        frontend for consistency

    Returns:
        Complete assessment with all metrics and recommendations
    """
    try:
        print(f"\n{'='*70}")
        print("🔄 ASSESS REQUEST RECEIVED")
        print(f"{'='*70}")
        print(f"👤 Age: {age}")
        print(f"📖 Paragraph length: {len(paragraph)} characters")
        print(f"🎵 Audio file: {audio_file.filename} ({audio_file.size} bytes)")
        print(f"🎤 Frontend recognized text received: '{recognized_text}'")
        if recognized_text:
            chars = len(recognized_text)
            words = len(recognized_text.split())
            print(f"   → Length: {chars} chars, {words} words")

        # Timing
        start_time = time.time()
        step_times = {}

        # Validate inputs
        if age < 5 or age > 100:
            detail = "Age must be between 5 and 100"
            raise HTTPException(status_code=400, detail=detail)

        if not paragraph or len(paragraph.strip()) < 5:
            detail = "Paragraph must be at least 5 characters"
            raise HTTPException(status_code=400, detail=detail)

        # More flexible file validation - accept any audio file
        if audio_file.filename:
            exts = ('.wav', '.mp3', '.webm')
            if not audio_file.filename.lower().endswith(exts):
                fn = audio_file.filename
                print(f"⚠️  File: {fn}")
            print(f"⚠️ File extension warning: {audio_file.filename}")

        # Read audio file
        print("📥 Reading audio file...")
        audio_bytes = await audio_file.read()
        step_times['read_audio'] = time.time()
        elapsed = time.time() - start_time
        print(f"✅ Audio file read: {len(audio_bytes)} bytes ({elapsed:.2f}s)")

        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        # PRIORITY 1: Use frontend Web Speech API if provided
        # This is the actual text the user said (captured live)
        if recognized_text and recognized_text.strip():
            txt_strip = recognized_text.strip()
            print(f"✅ Using frontend Web Speech API: '{txt_strip}'")
            final_recognized_text = txt_strip
            print("   → Actual words user spoke (captured live)")
            step_times['speech_recognition'] = time.time()
        else:
            # PRIORITY 2: Fallback to Vosk
            print("⚠️ No frontend, using Vosk...")
            filename = audio_file.filename or 'audio.wav'
            vosk_text = process_audio_file(audio_bytes, filename)
            step_times['speech_recognition'] = time.time()

            if vosk_text:
                print(f"✅ Vosk recognized: '{vosk_text}'")
                final_recognized_text = vosk_text
            else:
                print("❌ Neither frontend nor Vosk detected speech")
                final_recognized_text = "[No speech detected]"

        print(f"\n🎤 FINAL RECOGNIZED TEXT: '{final_recognized_text}'\n")

        # ========== Text Comparison ==========
        # Compare texts
        compare_start = time.time()
        comparison_result = compare_text(paragraph, final_recognized_text)
        step_times['text_comparison'] = time.time() - compare_start
        accuracy = comparison_result['accuracy_percent']
        duration = step_times['text_comparison']
        print(f"✅ Accuracy: {accuracy}% ({duration:.2f}s)")

        # ========== Reading Speed Analysis ==========
        speed_start = time.time()
        speed_analyzer = ReadingSpeedAnalyzer()
        spoken_words = len(final_recognized_text.split())

        # Estimate reading time from audio length (approximate)
        speed_analyzer.start_timer()
        elapsed = len(audio_bytes) / (16000 * 2)
        speed_analyzer.end_time = speed_analyzer.start_time + elapsed

        elapsed_time = speed_analyzer.get_elapsed_time()
        wpm = speed_analyzer.calculate_wpm(spoken_words)
        speed_category = speed_analyzer.get_reading_speed_category(wpm)
        step_times['speed_analysis'] = time.time() - speed_start

        et, wpm_v = elapsed_time, wpm
        dur = step_times['speed_analysis']
        print(f"⏱️ Time: {et:.2f}s, WPM: {wpm_v:.1f} ({dur:.2f}s)")

        # ========== Dyslexia Risk Scoring ==========
        print("📈 Calculating dyslexia risk...")
        risk_start = time.time()
        risk_scorer = DyslexiaRiskScorer()
        risk_assessment = risk_scorer.calculate_risk_score(
            wpm=wpm,
            accuracy_percent=comparison_result['accuracy_percent'],
            missing_words=comparison_result['missing_words'],
            wrong_words=comparison_result['wrong_words'],
            extra_words=comparison_result['extra_words'],
            total_words=comparison_result['total_words'],
            pause_count=0
        )
        step_times['risk_scoring'] = time.time() - risk_start
        level, ts = risk_assessment['risk_level'], step_times['risk_scoring']
        print(f"⚠️ Risk: {level} ({ts:.2f}s)")

        # ========== Generate Feedback ==========
        accuracy_pct = comparison_result['accuracy_percent']
        accuracy_feedback = get_performance_feedback(accuracy_pct)

        # Difficulty assessment
        if comparison_result['accuracy_percent'] >= 90:
            if wpm >= 120:
                difficulty = "✅ Excellent - Challenge harder"
            else:
                difficulty = "⚠️ Accurate - Build confidence"
        elif comparison_result['accuracy_percent'] >= 80:
            if wpm >= 120:
                difficulty = "👍 Good progress - Current level is appropriate"
            else:
                difficulty = "📚 Keep practicing at current level"
        elif comparison_result['accuracy_percent'] >= 70:
            if wpm >= 100:
                difficulty = "📖 Struggling - Try easier material for success"
            else:
                difficulty = "⚠️ Too difficult - Use simpler passages"
        else:
            difficulty = "🚩 Too challenging - Start with beginner passages"

        # ========== Generate Assistance Data ==========
        print("🆘 Generating assistance module data...")
        assistance_start = time.time()
        assistance_data = None

        has_errors = (comparison_result['wrong_words'] > 0 or
                      comparison_result['missing_words'] > 0)
        if tts_engine and has_errors:
            word_level_errors = comparison_result.get('word_level_errors', {})
            wrong_words = word_level_errors.get('wrong_words', [])
            missing_words = word_level_errors.get('missing_words', [])
            extra_words = word_level_errors.get('extra_words', [])

            assistance_data = AssistanceData(
                has_errors=True,
                error_count=len(wrong_words) + len(missing_words),
                wrong_words=[[w, c] for w, c in wrong_words],
                missing_words=missing_words,
                extra_words=extra_words,
                assistance_enabled=True
            )
            step_times['assistance'] = time.time() - assistance_start
            ec = assistance_data.error_count
            ts = step_times['assistance']
            print(f"✅ Assistance: {ec} errors ({ts:.2f}s)")
        else:
            assistance_data = AssistanceData(
                has_errors=False,
                error_count=0,
                wrong_words=[],
                missing_words=[],
                extra_words=[],
                assistance_enabled=tts_engine is not None
            )
            step_times['assistance'] = time.time() - assistance_start

        # ========== Build Response ==========
        print("✅ Building assessment response...")
        response = AssessmentResponse(
            reference_text=paragraph,
            recognized_text=final_recognized_text,
            age=age,
            speed_metrics=SpeedMetrics(
                elapsed_time_seconds=elapsed_time,
                elapsed_time_formatted=speed_analyzer.get_elapsed_time_formatted(),
                spoken_words=spoken_words,
                wpm=wpm,
                speed_category=speed_category['category'],
                speed_indicator=speed_category['indicator'],
                dyslexia_risk=speed_category['dyslexia_risk']
            ),
            accuracy_metrics=AccuracyMetrics(**comparison_result),
            accuracy_feedback=accuracy_feedback,
            difficulty_assessment=difficulty,
            risk_assessment=RiskAssessment(**risk_assessment),
            assistance=assistance_data,
            status="success"
        )

        # Print timing summary
        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print("⏱️ PERFORMANCE SUMMARY")
        print(f"{'='*70}")
        for step, duration in step_times.items():
            print(f"  {step:.<40} {duration:>8.2f}s")
        print(f"  {'TOTAL':.<40} {total_time:>8.2f}s")
        print(f"{'='*70}\n")

        print(f"{'='*70}")
        print("✅ ASSESSMENT COMPLETE")
        print(f"{'='*70}\n")

        # ========== Save to Database ==========
        try:
            print("💾 Saving assessment to database...")
            # Create or get user
            user_crud = UserCRUD(db)
            user = user_crud.get_by_email("guest@dyslexia.local")
            if not user:
                user = user_crud.create_user(
                    schemas.UserCreate(
                        username="guest",
                        email="guest@dyslexia.local",
                        age=age
                    )
                )
            else:
                # Update age if different
                user_crud.update_user(
                    user.id,
                    schemas.UserUpdate(age=age)
                )

            # Save assessment
            assessment = AssessmentCRUD.create_assessment(
                db,
                user.id,
                schemas.AssessmentCreate(
                    paragraph_text=paragraph,
                    recognized_text=final_recognized_text
                )
            )

            # Save assessment results
            result = ResultCRUD.create_result(
                db,
                assessment.id,
                schemas.AssessmentResultCreate(
                    wpm=wpm,
                    accuracy_percent=accuracy,
                    risk_score=risk_assessment['risk_score'],
                    risk_level=risk_assessment['risk_level'],
                    elapsed_time_seconds=elapsed_time,
                    total_words=comparison_result['total_words'],
                    correct_words=comparison_result['correct_words'],
                    wrong_words=comparison_result['wrong_words'],
                    missing_words=comparison_result['missing_words'],
                    extra_words=comparison_result['extra_words']
                )
            )

            # Update progress history
            ProgressCRUD.create_or_update_weekly_progress(db, user.id)

            print("✅ Assessment saved to database")
        except Exception as e:
            print(f"⚠️ Database save warning: {e}")
            # Don't fail the assessment if database save fails

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Assessment error: {str(e)}\n")
        msg = f"Assessment failed: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.post("/assess-text", response_model=AssessmentResponse)
async def assess_with_text(
    request: AssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Testing endpoint: Assessment with pre-recognized text
    (Use for testing without audio processing)

    Args:
        age: User age
        paragraph: Reference paragraph

    Returns:
        Assessment results based on provided text

    Note: This is for testing. In production, use /assess with audio file.
    """
    try:
        if request.age < 5 or request.age > 100:
            raise HTTPException(
                status_code=400,
                detail="Age: 5-100"
            )

        if not request.paragraph or len(request.paragraph.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Paragraph >= 5 chars"
            )

        # For testing, assume the recognized text is the same as reference
        recognized_text = request.paragraph

        # ========== Text Comparison ==========
        comparison_result = compare_text(request.paragraph, recognized_text)

        # ========== Reading Speed Analysis ==========
        speed_analyzer = ReadingSpeedAnalyzer()
        spoken_words = len(recognized_text.split())

        # For testing, assume 2 seconds per standard reading
        speed_analyzer.start_timer()
        speed_analyzer.end_time = speed_analyzer.start_time + 10

        elapsed_time = speed_analyzer.get_elapsed_time()
        wpm = speed_analyzer.calculate_wpm(spoken_words)
        speed_category = speed_analyzer.get_reading_speed_category(wpm)

        # ========== Dyslexia Risk Scoring ==========
        risk_scorer = DyslexiaRiskScorer()
        risk_assessment = risk_scorer.calculate_risk_score(
            wpm=wpm,
            accuracy_percent=comparison_result['accuracy_percent'],
            missing_words=comparison_result['missing_words'],
            wrong_words=comparison_result['wrong_words'],
            extra_words=comparison_result['extra_words'],
            total_words=comparison_result['total_words'],
            pause_count=0
        )

        # ========== Generate Feedback ==========
        accuracy_feedback = get_performance_feedback(comparison_result['accuracy_percent'])
        difficulty = "👍 Good progress - Current level is appropriate"

        # ========== Build Response ==========
        response = AssessmentResponse(
            reference_text=request.paragraph,
            recognized_text=recognized_text,
            age=request.age,
            speed_metrics=SpeedMetrics(
                elapsed_time_seconds=elapsed_time,
                elapsed_time_formatted=speed_analyzer.get_elapsed_time_formatted(),
                spoken_words=spoken_words,
                wpm=wpm,
                speed_category=speed_category['category'],
                speed_indicator=speed_category['indicator'],
                dyslexia_risk=speed_category['dyslexia_risk']
            ),
            accuracy_metrics=AccuracyMetrics(**comparison_result),
            accuracy_feedback=accuracy_feedback,
            difficulty_assessment=difficulty,
            risk_assessment=RiskAssessment(**risk_assessment),
            status="success"
        )

        # ========== Save to Database ==========
        try:
            # Create or get user
            user = UserCRUD.get_user_by_email(db, "guest@dyslexia.local")
            if not user:
                user = UserCRUD.create_user(
                    db,
                    schemas.UserCreate(
                        username="guest",
                        email="guest@dyslexia.local",
                        age=request.age
                    )
                )

            # Save assessment
            assessment = AssessmentCRUD.create_assessment(
                db,
                user.id,
                schemas.AssessmentCreate(
                    paragraph_text=request.paragraph,
                    recognized_text=recognized_text
                )
            )

            # Save assessment results
            ResultCRUD.create_result(
                db,
                assessment.id,
                schemas.AssessmentResultCreate(
                    wpm=wpm,
                    accuracy_percent=comparison_result['accuracy_percent'],
                    risk_score=risk_assessment['risk_score'],
                    risk_level=risk_assessment['risk_level'],
                    elapsed_time_seconds=elapsed_time,
                    total_words=comparison_result['total_words'],
                    correct_words=comparison_result['correct_words'],
                    wrong_words=comparison_result['wrong_words'],
                    missing_words=comparison_result['missing_words'],
                    extra_words=comparison_result['extra_words']
                )
            )

            # Update progress history
            ProgressCRUD.create_or_update_weekly_progress(db, user.id)
        except Exception as e:
            print(f"⚠️ Database save warning: {e}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


# ================== Pronunciation Training Endpoints ==================

@app.post("/pronunciation/word-audio")
async def get_word_pronunciation(word: str = Form(...)):
    """
    Get pronunciation audio for a word (for 'Hear it' button)

    Args:
        word: Word to pronounce

    Returns:
        WAV audio file or base64 encoded audio
    """
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")

        if not pronunciation_trainer or not tts_engine:
            raise HTTPException(status_code=503, detail="Pronunciation assistance not available")

        print(f"🎵 Generating pronunciation for: '{word}'")
        audio_bytes, audio_base64 = pronunciation_trainer.speak_word(word)

        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate pronunciation")

        # Return as streaming response for better browser support
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={word}_pronunciation.wav"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Pronunciation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate pronunciation: {str(e)}")


@app.post("/pronunciation/check", response_model=PronunciationCheckResult)
async def check_pronunciation(
    word: str = Form(...),
    audio_file: UploadFile = File(..., description="WAV audio of user attempting the word")
):
    """
    Check user's pronunciation of a word and provide feedback

    Process:
    1. Extract speech from audio using Vosk
    2. Compare with target word
    3. Provide feedback and similarity score

    Args:
        word: Target word to check pronunciation for
        audio_file: WAV audio of user's attempt

    Returns:
        Pronunciation check result with feedback
    """
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")

        if not pronunciation_trainer:
            raise HTTPException(status_code=503, detail="Pronunciation training not available")

        print(f"\n{'='*60}")
        print(f"🎯 PRONUNCIATION CHECK: '{word}'")
        print(f"{'='*60}")

        # Read audio file
        audio_bytes = await audio_file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        print(f"🎵 Audio file size: {len(audio_bytes)} bytes")

        # Run pronunciation training
        result = pronunciation_trainer.pronunciation_training(word, audio_bytes)

        # Prepare response
        return PronunciationCheckResult(
            word=word,
            recognized=result["recognized"],
            correct=result["correct"],
            is_correct=result["is_correct"],
            similarity_ratio=result["similarity_ratio"],
            feedback=result["feedback"],
            pronunciation_audio=result["pronunciation_audio"],
            raw_recognized=result["attempt_details"]["raw_recognized"],
            exact_match=result["attempt_details"]["exact_match"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Pronunciation Check Error: {e}")
        raise HTTPException(status_code=500, detail=f"Pronunciation check failed: {str(e)}")


@app.post("/pronunciation/word-comparison")
async def compare_words(
    spoken_word: str = Form(...),
    target_word: str = Form(...)
):
    """
    Compare two words for pronunciation similarity
    Useful for detailed analysis without audio processing

    Args:
        spoken_word: Word as spoken by user
        target_word: Correct target word

    Returns:
        Detailed comparison metrics
    """
    try:
        if not spoken_word or not target_word:
            raise HTTPException(status_code=400, detail="Both words are required")

        comparison = PronunciationComparator.compare_word(spoken_word, target_word)

        return {
            "spoken": spoken_word,
            "target": target_word,
            "is_exact_match": comparison["is_exact"],
            "similarity_ratio": comparison["similarity"],
            "confidence": comparison["confidence"],
            "details": comparison["details"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Comparison Error: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.post("/pronunciation/batch-check")
async def batch_check_pronunciations(
    words: str = Form(..., description="JSON array of words to check"),
    audio_files: list = []
):
    """
    Check pronunciation for multiple words (batch operation)

    Args:
        words: JSON array of target words
        audio_files: List of audio files (one per word)

    Returns:
        List of pronunciation check results
    """
    try:
        if not pronunciation_trainer:
            raise HTTPException(status_code=503, detail="Pronunciation training not available")

        # Parse words JSON
        try:
            word_list = json.loads(words)
            if not isinstance(word_list, list):
                raise ValueError("Words must be a JSON array")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for words")

        print(f"📚 Batch pronunciation check for {len(word_list)} words")

        results = []
        for word in word_list:
            if isinstance(word, str) and word.strip():
                # For batch, we'll just provide pronunciation and similarity without audio
                # In production, you'd correlate audio_files with words
                comparison = PronunciationComparator.compare_word("", word)

                results.append({
                    "word": word,
                    "status": "ready",
                    "feedback": f"Ready to practice pronunciation of '{word}'"
                })

        return {
            "total_words": len(word_list),
            "words": results
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Batch Check Error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch check failed: {str(e)}")


# ================== Speed Trainer Endpoints ==================

@app.post("/speed-trainer/prepare")
async def prepare_pace_reading_session(request: PaceReadingRequest):
    """
    Prepare text for guided pace reading training.

    Args:
        request: Text and optional custom speed levels

    Returns:
        Session data with words, timings, and initial configuration
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Create trainer instance
        trainer = SpeedTrainer()

        # Use custom speeds if provided, otherwise use defaults
        speeds = request.speeds or SpeedTrainer.DEFAULT_SPEEDS

        # Create session
        import uuid
        session_id = str(uuid.uuid4())[:8]

        session = trainer.create_session(request.text, speeds, session_id)

        # Store session globally
        speed_trainer_sessions[session_id] = trainer

        # Return session data
        session_data = trainer.get_session_data()
        session_data["session_id"] = session_id

        return PaceReadingResponse(
            text=session.text,
            words=session.words,
            total_words=session.total_words,
            speeds=speeds,
            intervals=[trainer.calculate_interval(wpm) for wpm in speeds],
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Speed Trainer Prepare Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare pace reading: {str(e)}")


@app.get("/speed-trainer/session/{session_id}")
async def get_session_data(session_id: str):
    """
    Get current session data (words, current position, round info)

    Args:
        session_id: ID of the training session

    Returns:
        Current session state and configuration
    """
    try:
        if session_id not in speed_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = speed_trainer_sessions[session_id]
        session_data = trainer.get_session_data()

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Speed Trainer Session Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session data: {str(e)}")


@app.post("/speed-trainer/action/{session_id}")
async def perform_session_action(session_id: str, action_request: SpeedTrainerAction):
    """
    Perform an action on the training session (start, pause, resume, reset, advance).

    Args:
        session_id: ID of the training session
        action_request: Action to perform and optional session_id

    Returns:
        Updated session state after action
    """
    try:
        if session_id not in speed_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = speed_trainer_sessions[session_id]
        action = action_request.action.lower()

        if action == "start":
            # Mark first round as in progress
            if trainer.session and trainer.session.rounds:
                trainer.session.rounds[0].status = "in_progress"
            result = "Training started"

        elif action == "pause":
            trainer.pause()
            result = "Training paused"

        elif action == "resume":
            trainer.resume()
            result = "Training resumed"

        elif action == "reset":
            trainer.reset()
            result = "Training reset to beginning"

        elif action == "advance_word":
            success = trainer.advance_to_next_word()
            result = "Advanced to next word" if success else "Training complete"

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

        # Return updated session data
        session_data = trainer.get_session_data()

        return {
            "action": action,
            "result": result,
            "session_data": session_data,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Speed Trainer Action Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform action: {str(e)}")


@app.get("/speed-trainer/stats/{session_id}")
async def get_session_stats(session_id: str):
    """
    Get statistics and progress of a training session.

    Args:
        session_id: ID of the training session

    Returns:
        Session statistics (words, rounds, progress, timing)
    """
    try:
        if session_id not in speed_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = speed_trainer_sessions[session_id]
        stats = trainer.get_session_stats()

        return stats

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Speed Trainer Stats Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.post("/speed-trainer/submit-results", response_model=SpeedTrainerCompletionResult)
async def submit_speed_trainer_results(request: SpeedTrainerResults):
    """
    Submit reading completion results and calculate final WPM.

    Args:
        request: Session ID and elapsed time in seconds

    Returns:
        Completion result with calculated WPM
    """
    try:
        session_id = request.session_id
        elapsed_time = request.elapsed_time_seconds

        if session_id not in speed_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = speed_trainer_sessions[session_id]
        session = trainer.session

        if not session:
            raise HTTPException(status_code=400, detail="Session data is invalid")

        # Calculate WPM based on actual elapsed time
        if elapsed_time > 0:
            calculated_wpm = (session.total_words / elapsed_time) * 60
        else:
            calculated_wpm = 0

        print(f"\n✅ SPEED TRAINER SESSION COMPLETED")
        print(f"   Session ID: {session_id}")
        print(f"   Total Words: {session.total_words}")
        print(f"   Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"   Calculated WPM: {calculated_wpm:.2f}")
        print(f"   Status: Completed")

        return SpeedTrainerCompletionResult(
            session_id=session_id,
            total_words=session.total_words,
            elapsed_time_seconds=elapsed_time,
            calculated_wpm=round(calculated_wpm, 2),
            status="completed",
            message=f"Great job! You read {session.total_words} words in {elapsed_time:.1f} seconds at {calculated_wpm:.0f} WPM"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Speed Trainer Results Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit results: {str(e)}")


# ================== Chunk Reading (Phrase Training) Endpoints ==================

@app.post("/chunk-reading/prepare", response_model=ChunkReadingResponse)
async def prepare_chunk_reading_session(request: ChunkReadingRequest):
    """
    Prepare text for chunk reading (phrase training).

    Args:
        request: Text and optional phrase length configuration

    Returns:
        Session data with phrases and initial configuration
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Create trainer instance
        min_len = request.min_phrase_length or 2
        max_len = request.max_phrase_length or 4
        trainer = PhraseTrainer(min_length=min_len, max_length=max_len)

        # Create session
        import uuid
        session_id = str(uuid.uuid4())[:8]

        session = trainer.create_session(request.text, session_id)

        # Store session globally
        phrase_trainer_sessions[session_id] = trainer

        print(f"✅ Chunk Reading Session Created")
        print(f"   Session ID: {session_id}")
        print(f"   Total Phrases: {session.total_phrases}")
        print(f"   Phrase Range: {min_len}-{max_len} words")

        return ChunkReadingResponse(
            text=session.text,
            phrases=session.phrases,
            total_phrases=session.total_phrases,
            min_phrase_length=min_len,
            max_phrase_length=max_len,
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chunk Reading Prepare Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare chunk reading: {str(e)}")


@app.get("/chunk-reading/session/{session_id}", response_model=ChunkReadingSession)
async def get_chunk_reading_session(session_id: str):
    """
    Get current chunk reading session data.

    Args:
        session_id: ID of the training session

    Returns:
        Current session state and configuration
    """
    try:
        if session_id not in phrase_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = phrase_trainer_sessions[session_id]
        session_data = trainer.get_session_data()

        return ChunkReadingSession(
            text=session_data["text"],
            phrases=session_data["phrases"],
            total_phrases=session_data["total_phrases"],
            current_phrase_index=session_data["current_phrase_index"],
            current_phrase=session_data["current_phrase"],
            is_paused=session_data["is_paused"],
            is_completed=session_data["is_completed"],
            session_id=session_data["session_id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chunk Reading Session Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session data: {str(e)}")


@app.post("/chunk-reading/action/{session_id}")
async def perform_chunk_reading_action(session_id: str, action_request: ChunkReadingAction):
    """
    Perform an action on the chunk reading session.

    Args:
        session_id: ID of the training session
        action_request: Action to perform (start, pause, resume, reset, advance_phrase)

    Returns:
        Updated session state after action
    """
    try:
        if session_id not in phrase_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = phrase_trainer_sessions[session_id]
        action = action_request.action.lower()

        if action == "start":
            # Mark session as started
            result = "Chunk reading started"

        elif action == "pause":
            trainer.pause()
            result = "Training paused"

        elif action == "resume":
            trainer.resume()
            result = "Training resumed"

        elif action == "reset":
            trainer.reset()
            result = "Training reset to beginning"

        elif action == "advance_phrase":
            success = trainer.advance_to_next_phrase()
            result = "Advanced to next phrase" if success else "Training complete"

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

        # Return updated session data
        session_data = trainer.get_session_data()

        return {
            "action": action,
            "result": result,
            "session_data": {
                "text": session_data["text"],
                "phrases": session_data["phrases"],
                "total_phrases": session_data["total_phrases"],
                "current_phrase_index": session_data["current_phrase_index"],
                "current_phrase": session_data["current_phrase"],
                "is_paused": session_data["is_paused"],
                "is_completed": session_data["is_completed"],
                "session_id": session_data["session_id"]
            },
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chunk Reading Action Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform action: {str(e)}")


@app.get("/chunk-reading/stats/{session_id}", response_model=ChunkReadingStats)
async def get_chunk_reading_stats(session_id: str):
    """
    Get statistics and progress of a chunk reading session.

    Args:
        session_id: ID of the training session

    Returns:
        Session statistics (phrases, progress, completion)
    """
    try:
        if session_id not in phrase_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = phrase_trainer_sessions[session_id]
        stats = trainer.get_session_stats()

        return ChunkReadingStats(
            total_phrases=stats["total_phrases"],
            current_phrase_index=stats["current_phrase_index"],
            phrases_completed=stats["phrases_completed"],
            progress_percent=stats["progress_percent"],
            is_completed=stats["is_completed"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chunk Reading Stats Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.post("/chunk-reading/submit-results", response_model=ChunkReadingCompletionResult)
async def submit_chunk_reading_results(request: ChunkReadingResults):
    """
    Submit chunk reading completion results and calculate metrics.

    Args:
        request: Session ID and elapsed time in seconds

    Returns:
        Completion result with calculated WPM and phrases/second
    """
    try:
        session_id = request.session_id
        elapsed_time = request.elapsed_time_seconds

        if session_id not in phrase_trainer_sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        trainer = phrase_trainer_sessions[session_id]
        session = trainer.session

        if not session:
            raise HTTPException(status_code=400, detail="Session data is invalid")

        # Count total words in all phrases
        total_words = sum(len(phrase.split()) for phrase in session.phrases)

        # Calculate metrics based on actual elapsed time
        if elapsed_time > 0:
            calculated_wpm = (total_words / elapsed_time) * 60
            phrases_per_second = session.total_phrases / elapsed_time
        else:
            calculated_wpm = 0
            phrases_per_second = 0

        print(f"\n✅ CHUNK READING SESSION COMPLETED")
        print(f"   Session ID: {session_id}")
        print(f"   Total Phrases: {session.total_phrases}")
        print(f"   Total Words: {total_words}")
        print(f"   Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"   Calculated WPM: {calculated_wpm:.2f}")
        print(f"   Phrases/Second: {phrases_per_second:.2f}")

        return ChunkReadingCompletionResult(
            session_id=session_id,
            total_phrases=session.total_phrases,
            total_words=total_words,
            elapsed_time_seconds=elapsed_time,
            calculated_wpm=round(calculated_wpm, 2),
            phrases_per_second=round(phrases_per_second, 2),
            status="completed",
            message=f"Excellent! You read {session.total_phrases} phrases ({total_words} words) in {elapsed_time:.1f} seconds at {calculated_wpm:.0f} WPM"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chunk Reading Results Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit results: {str(e)}")


# ================== Error Handlers ==================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "status": "error",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
