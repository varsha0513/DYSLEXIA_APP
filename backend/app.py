"""
FastAPI Backend API for Dyslexia Assessment System
Wraps the complete reading assessment pipeline into REST endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
import wave
import json
import os
from vosk import Model, KaldiRecognizer
from text_comparison import compare_text, get_performance_feedback
from reading_speed import ReadingSpeedAnalyzer
from dyslexia_risk_scoring import DyslexiaRiskScorer

# Initialize FastAPI
app = FastAPI(
    title="Dyslexia Assessment API",
    description="API for comprehensive dyslexia risk assessment through reading analysis",
    version="1.0.0"
)

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
    raise RuntimeError(f"❌ Vosk model not found at {model_path}. Please download it first.")

model = Model(model_path)


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
    status: str = "success"


# ================== Helper Functions ==================

def process_audio_file(audio_bytes: bytes) -> str:
    """
    Process audio file and extract recognized text using Vosk
    
    Args:
        audio_bytes: Raw audio data
        
    Returns:
        Recognized text from the audio
    """
    try:
        # Read WAV file
        audio_stream = io.BytesIO(audio_bytes)
        with wave.open(audio_stream, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            
            print(f"📊 Audio properties - Channels: {channels}, SampleWidth: {sample_width}, SampleRate: {sample_rate}")
            
            # Log properties for debugging
            if channels != 1:
                print(f"⚠️ Warning: Expected mono (1 channel), got {channels} channels")
            if sample_width != 2:
                print(f"⚠️ Warning: Expected 16-bit (2 bytes), got {sample_width} bytes")
            if sample_rate != 16000:
                print(f"⚠️ Warning: Expected 16000 Hz, got {sample_rate} Hz")
            
            # Use Vosk recognizer
            recognizer = KaldiRecognizer(model, 16000)
            recognized_text = ""
            
            # Process audio in chunks
            frames_processed = 0
            while True:
                data = wav_file.readframes(4000)
                if len(data) == 0:
                    break
                
                frames_processed += 1
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        recognized_text = result.get("text", "")
                        print(f"📝 Recognized (interim): {recognized_text}")
            
            # Get final result
            result = json.loads(recognizer.FinalResult())
            final_text = result.get("text", "")
            
            print(f"📝 Final recognized text: {final_text}")
            print(f"📊 Processed {frames_processed} frames")
            
            if not final_text:
                print("⚠️ No speech detected in audio")
            
            return final_text.strip()
    
    except Exception as e:
        print(f"❌ Audio processing error: {str(e)}")
        raise ValueError(f"Failed to process audio: {str(e)}")


# ================== API Endpoints ==================

@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "name": "Dyslexia Assessment API",
        "version": "1.0.0",
        "status": "🟢 Running",
        "endpoints": {
            "assess_with_audio": "POST /assess - Send paragraph, age, and audio file",
            "assess_with_text": "POST /assess-text - Send paragraph, age, and recognized text (for testing)",
            "health": "GET /health - Health status"
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
    audio_file: UploadFile = File(..., description="WAV audio file of user reading the paragraph")
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
        
    Returns:
        Complete assessment with all metrics and recommendations
    """
    try:
        print(f"\n{'='*70}")
        print(f"🔄 ASSESS REQUEST RECEIVED")
        print(f"{'='*70}")
        print(f"👤 Age: {age}")
        print(f"📖 Paragraph length: {len(paragraph)} characters")
        print(f"🎵 Audio file: {audio_file.filename} ({audio_file.size} bytes)")
        
        # Validate inputs
        if age < 5 or age > 100:
            raise HTTPException(status_code=400, detail="Age must be between 5 and 100")
        
        if not paragraph or len(paragraph.strip()) < 5:
            raise HTTPException(status_code=400, detail="Paragraph must be at least 5 characters")
        
        # More flexible file validation - accept any audio file
        if audio_file.filename and not audio_file.filename.lower().endswith(('.wav', '.mp3', '.webm')):
            print(f"⚠️ File extension warning: {audio_file.filename}")
        
        # Read audio file
        print("📥 Reading audio file...")
        audio_bytes = await audio_file.read()
        print(f"✅ Audio file read: {len(audio_bytes)} bytes")
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        # Process audio to get recognized text
        print("🎤 Processing audio with Vosk...")
        recognized_text = process_audio_file(audio_bytes)
        
        if not recognized_text:
            print("⚠️ No speech detected - using silent recognition")
            # Don't fail if no speech - allow assessment to continue
            recognized_text = "[No speech detected - silence in audio]"
        
        print(f"✅ Recognition complete: {recognized_text}")
        
        # ========== Text Comparison ==========
        print("📊 Comparing texts...")
        comparison_result = compare_text(paragraph, recognized_text)
        print(f"✅ Accuracy: {comparison_result['accuracy_percent']}%")
        
        # ========== Reading Speed Analysis ==========
        speed_analyzer = ReadingSpeedAnalyzer()
        spoken_words = len(recognized_text.split())
        
        # Estimate reading time from audio length (approximate)
        audio_length_seconds = len(audio_bytes) / (16000 * 2)  # 16kHz, 16-bit
        speed_analyzer.start_timer()
        speed_analyzer.end_time = speed_analyzer.start_time + audio_length_seconds
        
        elapsed_time = speed_analyzer.get_elapsed_time()
        wpm = speed_analyzer.calculate_wpm(spoken_words)
        speed_category = speed_analyzer.get_reading_speed_category(wpm)
        
        print(f"⏱️ Reading time: {elapsed_time:.2f}s, WPM: {wpm:.1f}")
        
        # ========== Dyslexia Risk Scoring ==========
        print("📈 Calculating dyslexia risk...")
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
        print(f"⚠️ Risk Level: {risk_assessment['risk_level']}")
        
        # ========== Generate Feedback ==========
        accuracy_feedback = get_performance_feedback(comparison_result['accuracy_percent'])
        
        # Difficulty assessment
        if comparison_result['accuracy_percent'] >= 90:
            if wpm >= 120:
                difficulty = "✅ Excellent reader - Challenge with harder passages"
            else:
                difficulty = "⚠️ Accurate but slow - May need confidence building"
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
        
        # ========== Build Response ==========
        print("✅ Building assessment response...")
        response = AssessmentResponse(
            reference_text=paragraph,
            recognized_text=recognized_text,
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
            status="success"
        )
        
        print(f"{'='*70}")
        print(f"✅ ASSESSMENT COMPLETE - SENDING RESPONSE")
        print(f"{'='*70}\n")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ASSESSMENT ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/assess-text", response_model=AssessmentResponse)
async def assess_with_text(request: AssessmentRequest):
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
            raise HTTPException(status_code=400, detail="Age must be between 5 and 100")
        
        if not request.paragraph or len(request.paragraph.strip()) < 5:
            raise HTTPException(status_code=400, detail="Paragraph must be at least 5 characters")
        
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
        return AssessmentResponse(
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
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


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
