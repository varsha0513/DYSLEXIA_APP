"""
FastAPI Backend API for Dyslexia Assessment System
Wraps the complete reading assessment pipeline into REST endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
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

# Initialize TTS Engine for Assistance Module
try:
    tts_engine = DyslexiaAssistanceEngine(rate=100, volume=0.9)
    print("✅ Assistance Module (TTS) ready")
except Exception as e:
    print(f"⚠️ TTS Engine initialization warning: {e}")
    tts_engine = None


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
        print(f"🎵 Processing audio file: {filename}")
        print(f"📊 Total audio bytes received: {len(audio_bytes)}")
        
        # Validate audio has content
        if len(audio_bytes) < 100:
            print(f"❌ Audio file too small: {len(audio_bytes)} bytes")
            return ""
        
        # Read WAV file
        audio_stream = io.BytesIO(audio_bytes)
        with wave.open(audio_stream, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            
            print(f"📊 WAV Properties:")
            print(f"   - Channels: {channels}")
            print(f"   - Sample Width: {sample_width} bytes (16-bit = 2)")
            print(f"   - Sample Rate: {sample_rate} Hz")
            print(f"   - Frames: {num_frames}")
            print(f"   - Duration: {num_frames / sample_rate:.2f} seconds")
            
            # Validate audio format
            if channels != 1:
                print(f"⚠️ Converting {channels} channels to mono...")
            if sample_width != 2:
                print(f"⚠️ Expected 16-bit audio, got {sample_width*8}-bit")
            
            # Check if audio has actual sound (rough estimate)
            audio_data = wav_file.readframes(num_frames)
            if len(audio_data) < 100:
                print(f"❌ Audio data is too small: {len(audio_data)} bytes")
                print("   → Audio is likely silent or corrupted")
                return ""
            
            # Reset stream for recognition
            audio_stream.seek(0)
            
            # Create recognizer - Vosk model expects 16kHz mono
            if sample_rate != 16000:
                print(f"⚠️ Vosk needs 16000 Hz, audio is {sample_rate} Hz")
                # Vosk can handle other rates, but 16000 is optimal
            
            print(f"🎤 Creating Vosk recognizer (target: 16000 Hz)...")
            recognizer = KaldiRecognizer(model, sample_rate)
            recognizer.SetWords(None)  # Use default word list
            
            # Process audio in optimal chunk size for Vosk
            frames_processed = 0
            chunks_with_results = 0
            interim_results = []
            
            print("📥 Feeding audio to Vosk recognizer...")
            with wave.open(audio_stream, 'rb') as wav_file:
                while True:
                    # Use larger chunks for better recognition (4000 bytes = 1000 samples @ 16-bit)
                    data = wav_file.readframes(4096)
                    if len(data) == 0:
                        break
                    
                    # Feed data to recognizer
                    try:
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            if result.get("text"):
                                interim_results.append(result.get("text"))
                                chunks_with_results += 1
                                print(f"✅ Interim result #{chunks_with_results}: {result.get('text')}")
                    except Exception as e:
                        print(f"⚠️ Error processing chunk: {e}")
                    
                    frames_processed += 1
                    if frames_processed % 5 == 0:
                        print(f"📊 Processed {frames_processed} chunks...")
            
            # Get final result
            try:
                final_result = json.loads(recognizer.FinalResult())
                final_text = final_result.get("text", "")
            except Exception as e:
                print(f"⚠️ Error getting final result: {e}")
                final_text = ""
            
            print(f"\n🎤 VOSK RECOGNITION RESULTS:")
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
                print("\n❌ NO SPEECH RECOGNIZED")
                print("   Possible causes:")
                print("   1. ⚠️ Audio is truly silent (check microphone volume)")
                print("   2. ⚠️ Audio format is corrupted (resampling failed?)")
                print("   3. ⚠️ Speech is in different language/heavy accent")
                print("   4. ⚠️ Audio envelope is wrong (too soft to detect)")
            
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
            raise HTTPException(status_code=503, detail="TTS Engine not available")
        
        print(f"🔊 Generating pronunciation for: '{word}'")
        audio_bytes, _ = tts_engine.generate_audio_file(word)
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={word}.wav"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.post("/tts/correction")
async def get_word_correction(wrong_word: str = Form(...), correct_word: str = Form(...)):
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
            raise HTTPException(status_code=503, detail="TTS Engine not available")
        
        print(f"🆘 Generating correction: '{wrong_word}' → '{correct_word}'")
        assistance = tts_engine.generate_word_assistance(wrong_word, correct_word)
        
        return assistance
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Correction Error: {e}")
        raise HTTPException(status_code=500, detail=f"Correction generation failed: {str(e)}")


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
            "tts_word": "POST /tts/word - Generate audio pronunciation for a word",
            "tts_correction": "POST /tts/correction - Get word correction with audio assistance",
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
    audio_file: UploadFile = File(..., description="WAV audio file of user reading the paragraph"),
    recognized_text: str = Form(default='', description="Optional: Pre-recognized text from frontend Web Speech API")
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
        recognized_text: Optional pre-recognized text from frontend for consistency
        
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
        print(f"🎤 Frontend recognized text received: '{recognized_text}'")
        if recognized_text:
            print(f"   → Length: {len(recognized_text)} chars, {len(recognized_text.split())} words")
        
        # Timing
        start_time = time.time()
        step_times = {}
        
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
        step_times['read_audio'] = time.time()
        print(f"✅ Audio file read: {len(audio_bytes)} bytes ({(time.time()-start_time):.2f}s)")
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        # PRIORITY 1: Use frontend Web Speech API recognition if provided (it's working!)
        # This is the ACTUAL text the user said, captured in real-time
        if recognized_text and recognized_text.strip():
            print(f"✅ Using frontend Web Speech API recognition: '{recognized_text.strip()}'")
            final_recognized_text = recognized_text.strip()
            print(f"   → This is the actual words user spoke (captured live)")
            step_times['speech_recognition'] = time.time()
        else:
            # PRIORITY 2: Fallback to Vosk only if frontend didn't capture anything
            print("⚠️ No frontend recognition provided, trying Vosk as fallback...")
            filename = audio_file.filename or 'audio.wav'
            vosk_text = process_audio_file(audio_bytes, filename)
            step_times['speech_recognition'] = time.time()
            
            if vosk_text:
                print(f"✅ Vosk recognized: '{vosk_text}'")
                final_recognized_text = vosk_text
            else:
                print("❌ Neither frontend nor Vosk detected speech")
                final_recognized_text = "[No speech detected - silence in audio]"
        
        print(f"\n🎤 FINAL RECOGNIZED TEXT: '{final_recognized_text}'\n")
        
        # ========== Text Comparison ==========
        print("📊 Comparing texts...")
        compare_start = time.time()
        comparison_result = compare_text(paragraph, final_recognized_text)
        step_times['text_comparison'] = time.time() - compare_start
        print(f"✅ Accuracy: {comparison_result['accuracy_percent']}% ({step_times['text_comparison']:.2f}s)")
        
        # ========== Reading Speed Analysis ==========
        speed_start = time.time()
        speed_analyzer = ReadingSpeedAnalyzer()
        spoken_words = len(final_recognized_text.split())
        
        # Estimate reading time from audio length (approximate)
        audio_length_seconds = len(audio_bytes) / (16000 * 2)  # 16kHz, 16-bit
        speed_analyzer.start_timer()
        speed_analyzer.end_time = speed_analyzer.start_time + audio_length_seconds
        
        elapsed_time = speed_analyzer.get_elapsed_time()
        wpm = speed_analyzer.calculate_wpm(spoken_words)
        speed_category = speed_analyzer.get_reading_speed_category(wpm)
        step_times['speed_analysis'] = time.time() - speed_start
        
        print(f"⏱️ Reading time: {elapsed_time:.2f}s, WPM: {wpm:.1f} ({step_times['speed_analysis']:.2f}s)")
        
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
        print(f"⚠️ Risk Level: {risk_assessment['risk_level']} ({step_times['risk_scoring']:.2f}s)")
        
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
        
        # ========== Generate Assistance Data ==========
        print("🆘 Generating assistance module data...")
        assistance_start = time.time()
        assistance_data = None
        
        if tts_engine and (comparison_result['wrong_words'] > 0 or comparison_result['missing_words'] > 0):
            word_level_errors = comparison_result.get('word_level_errors', {})
            wrong_words = word_level_errors.get('wrong_words', [])
            missing_words = word_level_errors.get('missing_words', [])
            extra_words = word_level_errors.get('extra_words', [])
            
            assistance_data = AssistanceData(
                has_errors=True,
                error_count=len(wrong_words) + len(missing_words),
                wrong_words=[[w, c] for w, c in wrong_words],  # Convert tuples to lists for JSON
                missing_words=missing_words,
                extra_words=extra_words,
                assistance_enabled=True
            )
            step_times['assistance'] = time.time() - assistance_start
            print(f"✅ Assistance data generated: {assistance_data.error_count} errors found ({step_times['assistance']:.2f}s)")
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
        response_start = time.time()
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
        print(f"⏱️ PERFORMANCE SUMMARY")
        print(f"{'='*70}")
        for step, duration in step_times.items():
            print(f"  {step:.<40} {duration:>8.2f}s")
        print(f"  {'TOTAL':.<40} {total_time:>8.2f}s")
        print(f"{'='*70}\n")
        
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
