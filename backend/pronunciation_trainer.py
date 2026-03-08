"""
Pronunciation Assistance Module for Dyslexia Support Application

Provides functionality to help users learn correct pronunciation of words they misread:
1. Pronounce the correct word (text-to-speech)
2. Listen to user's attempt (speech-to-text)
3. Compare pronunciation against target
4. Provide feedback and retry if needed
"""

import io
import json
import wave
from typing import Dict, Tuple, Optional
from vosk import Model, KaldiRecognizer
import difflib


class PronunciationTrainer:
    """
    Manages pronunciation training for individual words.
    Orchestrates the workflow: speak → listen → compare → feedback
    """
    
    def __init__(self, vosk_model: Model, tts_engine=None):
        """
        Initialize the pronunciation trainer
        
        Args:
            vosk_model: Loaded Vosk Model instance for speech recognition
            tts_engine: Optional TTS engine instance for feedback
        """
        self.vosk_model = vosk_model
        self.tts_engine = tts_engine
        self.max_attempts = 3
    
    def normalize_word(self, word: str) -> str:
        """
        Normalize a word for comparison (lowercase, remove special chars)
        
        Args:
            word: Word to normalize
            
        Returns:
            Normalized word
        """
        return word.lower().strip()
    
    def speak_word(self, word: str, rate: int = 100) -> Tuple[bytes, str]:
        """
        Convert a word to speech using TTS engine.
        
        Args:
            word: Word to pronounce
            rate: Speech rate (50-300, default 100)
            
        Returns:
            Tuple of (audio_bytes, audio_base64_string) or empty if TTS not available
        """
        if not self.tts_engine:
            print(f"⚠️ TTS engine not available, cannot pronounce '{word}'")
            return b'', ''
        
        try:
            audio_bytes, audio_base64 = self.tts_engine.generate_audio_file(word)
            if audio_bytes:
                print(f"✅ Generated pronunciation for '{word}'")
                return audio_bytes, audio_base64
            else:
                print(f"❌ Failed to generate audio for '{word}'")
                return b'', ''
        except Exception as e:
            print(f"❌ Error speaking word '{word}': {e}")
            return b'', ''
    
    def listen_word(self, audio_bytes: bytes, duration_ms: int = 5000) -> str:
        """
        Convert user's spoken audio to text using Vosk speech recognition.
        
        Args:
            audio_bytes: Raw WAV audio data from user
            duration_ms: Expected duration of audio (for logging)
            
        Returns:
            Recognized text from the audio
        """
        try:
            if len(audio_bytes) < 100:
                print(f"⚠️ Audio too short ({len(audio_bytes)} bytes)")
                return ""
            
            # Parse the WAV file
            audio_stream = io.BytesIO(audio_bytes)
            try:
                with wave.open(audio_stream, 'rb') as wav_file:
                    sample_rate = wav_file.getframerate()
                    num_frames = wav_file.getnframes()
                    duration = num_frames / sample_rate if sample_rate > 0 else 0
                    
                    print(f"🎵 Processing audio: {duration:.2f}s @ {sample_rate}Hz")
                    
                    # Create recognizer
                    recognizer = KaldiRecognizer(self.vosk_model, sample_rate)
                    
                    # Feed audio to recognizer
                    audio_stream.seek(0)
                    recognized_text = ""
                    
                    with wave.open(audio_stream, 'rb') as wav_file:
                        while True:
                            data = wav_file.readframes(4096)
                            if len(data) == 0:
                                break
                            
                            if recognizer.AcceptWaveform(data):
                                result = json.loads(recognizer.Result())
                                recognized_text = result.get("text", "")
                    
                    # Get final result
                    final_result = json.loads(recognizer.FinalResult())
                    final_text = final_result.get("text", "")
                    
                    if final_text:
                        recognized_text = final_text
                    
                    if recognized_text:
                        print(f"✅ Recognized: '{recognized_text}'")
                    else:
                        print("❌ No speech recognized")
                    
                    return recognized_text
                    
            except Exception as e:
                print(f"❌ Error parsing audio: {e}")
                return ""
        
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            return ""
    
    def check_pronunciation(self, recognized_word: str, correct_word: str) -> Dict:
        """
        Compare recognized word with the correct word.
        Uses multiple comparison methods for flexibility.
        
        Args:
            recognized_word: Word recognized from user's speech
            correct_word: The correct target word
            
        Returns:
            Dict with comparison results and similarity metrics
        """
        norm_recognized = self.normalize_word(recognized_word)
        norm_correct = self.normalize_word(correct_word)
        
        # Exact match
        is_exact_match = norm_recognized == norm_correct
        
        # Similarity ratio using difflib
        similarity_ratio = difflib.SequenceMatcher(
            None, norm_recognized, norm_correct
        ).ratio()
        
        # Consider it correct if:
        # 1. Exact match, OR
        # 2. Similarity > 0.85 (allows minor misspellings)
        is_correct = is_exact_match or similarity_ratio > 0.85
        
        result = {
            "recognized": recognized_word,
            "correct": correct_word,
            "normalized_recognized": norm_recognized,
            "normalized_correct": norm_correct,
            "is_exact_match": is_exact_match,
            "similarity_ratio": round(similarity_ratio, 3),
            "is_correct": is_correct,
            "feedback": self._get_pronunciation_feedback(
                is_correct, similarity_ratio, norm_correct
            )
        }
        
        return result
    
    def _get_pronunciation_feedback(
        self, 
        is_correct: bool, 
        similarity_ratio: float,
        correct_word: str
    ) -> str:
        """
        Generate feedback message based on comparison result.
        
        Args:
            is_correct: Whether pronunciation was correct
            similarity_ratio: Similarity score (0-1)
            correct_word: The correct word
            
        Returns:
            Feedback message
        """
        if is_correct:
            return f"🎉 Perfect! You pronounced '{correct_word}' correctly!"
        elif similarity_ratio > 0.7:
            return (f"📍 Close! You said something like '{correct_word}' "
                   f"but not quite right. Try again.")
        else:
            return f"❌ That doesn't sound like '{correct_word}'. Let's try again!"
    
    def pronunciation_training(
        self, 
        word: str, 
        user_audio_bytes: bytes,
        max_attempts: Optional[int] = None
    ) -> Dict:
        """
        Complete pronunciation training workflow:
        1. Pronounce the word
        2. Listen to user attempt
        3. Check pronunciation
        4. Return feedback
        
        Args:
            word: Word to train pronunciation for
            user_audio_bytes: Raw WAV audio from user's attempt
            max_attempts: Maximum attempts (default: 3)
            
        Returns:
            Dict with training session results including:
            - is_correct: Whether pronunciation was correct
            - feedback: Message for user
            - recognized_word: What was recognized
            - similarity_ratio: How close the pronunciation was
            - attempt_details: Details of this attempt
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        
        print(f"\n{'='*60}")
        print(f"🎯 PRONUNCIATION TRAINING: '{word}'")
        print(f"{'='*60}")
        
        # Step 1: Pronounce the word
        print(f"\n1️⃣ Speaking the word...")
        audio_bytes, audio_base64 = self.speak_word(word)
        
        # Step 2: Listen to user's attempt
        print(f"2️⃣ Analyzing user's pronunciation...")
        recognized_word = self.listen_word(user_audio_bytes)
        
        # Step 3: Compare pronunciation
        print(f"3️⃣ Comparing pronunciation...")
        comparison = self.check_pronunciation(recognized_word, word)
        
        # Step 4: Return results
        result = {
            "word": word,
            "is_correct": comparison["is_correct"],
            "recognized": comparison["normalized_recognized"],
            "correct": comparison["normalized_correct"],
            "similarity_ratio": comparison["similarity_ratio"],
            "feedback": comparison["feedback"],
            "pronunciation_audio": audio_base64,  # For "Hear it" button response
            "attempt_details": {
                "raw_recognized": recognized_word,
                "exact_match": comparison["is_exact_match"],
                "similarity_ratio": comparison["similarity_ratio"]
            }
        }
        
        print(f"\n📊 RESULT:")
        print(f"   Recognized: {comparison['normalized_recognized']}")
        print(f"   Correct: {comparison['normalized_correct']}")
        print(f"   Match: {result['is_correct']}")
        print(f"   Similarity: {comparison['similarity_ratio']}")
        print(f"\n💬 FEEDBACK: {comparison['feedback']}")
        print(f"{'='*60}\n")
        
        return result
    
    def training_session(
        self,
        word: str,
        user_attempts: list
    ) -> Dict:
        """
        Run a complete training session with multiple attempts.
        Continues until word is pronounced correctly or max attempts reached.
        
        Args:
            word: Word to train
            user_attempts: List of audio_bytes for each attempt
            
        Returns:
            Dict with session summary including:
            - word: The trained word
            - success: Whether pronunciation was mastered
            - attempts: List of attempt results
            - total_attempts: Number of attempts made
            - final_status: Success or exceeded max attempts
        """
        print(f"\n{'='*70}")
        print(f"📚 PRONUNCIATION TRAINING SESSION: '{word}'")
        print(f"{'='*70}")
        
        attempts = []
        success = False
        
        for attempt_num, audio_bytes in enumerate(user_attempts, 1):
            print(f"\n🔄 ATTEMPT {attempt_num}/{len(user_attempts)}")
            
            result = self.pronunciation_training(word, audio_bytes)
            result["attempt_number"] = attempt_num
            attempts.append(result)
            
            if result["is_correct"]:
                success = True
                print(f"✅ SUCCESS on attempt {attempt_num}!")
                break
            
            if attempt_num < len(user_attempts):
                print(f"\n⏳ Preparing for next attempt...")
                # Speak the word again for retry
                audio_bytes, audio_base64 = self.speak_word(word)
        
        session_result = {
            "word": word,
            "success": success,
            "attempts": attempts,
            "total_attempts": len(attempts),
            "final_status": "success" if success else "exceeded_max_attempts",
            "summary": {
                "word": word,
                "mastered": success,
                "attempts_needed": len(attempts),
                "final_feedback": (
                    f"🎉 Excellent! You've mastered the pronunciation of '{word}'!"
                    if success
                    else f"💪 Keep practicing '{word}'! You're getting closer."
                )
            }
        }
        
        print(f"\n{'='*70}")
        print(f"📈 SESSION SUMMARY")
        print(f"   Word: {word}")
        print(f"   Status: {session_result['final_status'].replace('_', ' ').title()}")
        print(f"   Attempts: {len(attempts)}")
        print(f"   Result: {session_result['summary']['final_feedback']}")
        print(f"{'='*70}\n")
        
        return session_result


class PronunciationComparator:
    """
    Utility class for comparing words and providing detailed metrics.
    Can be used independently for word-level comparisons.
    """
    
    @staticmethod
    def compare_word(spoken: str, target: str) -> Dict:
        """
        Compare a spoken word against a target word.
        
        Args:
            spoken: The word as spoken/recognized
            target: The correct target word
            
        Returns:
            Dict with comparison details
        """
        def normalize(word):
            return word.lower().strip()
        
        spoken_norm = normalize(spoken)
        target_norm = normalize(target)
        
        # Calculate metrics
        is_exact = spoken_norm == target_norm
        similarity = difflib.SequenceMatcher(
            None, spoken_norm, target_norm
        ).ratio()
        
        # Determine confidence
        if is_exact:
            confidence = "high"
        elif similarity > 0.85:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "is_exact": is_exact,
            "similarity": round(similarity, 3),
            "confidence": confidence,
            "details": {
                "spoken": spoken,
                "target": target,
                "spoken_normalized": spoken_norm,
                "target_normalized": target_norm
            }
        }
    
    @staticmethod
    def get_pronunciation_distance(word1: str, word2: str) -> int:
        """
        Calculate edit distance (Levenshtein distance) between two words.
        Lower distance = more similar pronunciation.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Edit distance as integer
        """
        def normalize(word):
            return word.lower().strip()
        
        w1 = normalize(word1)
        w2 = normalize(word2)
        
        # Create matrix for edit distance calculation
        matrix = [[0] * (len(w2) + 1) for _ in range(len(w1) + 1)]
        
        for i in range(len(w1) + 1):
            matrix[i][0] = i
        for j in range(len(w2) + 1):
            matrix[0][j] = j
        
        for i in range(1, len(w1) + 1):
            for j in range(1, len(w2) + 1):
                if w1[i-1] == w2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = 1 + min(
                        matrix[i-1][j],      # deletion
                        matrix[i][j-1],      # insertion
                        matrix[i-1][j-1]     # substitution
                    )
        
        return matrix[len(w1)][len(w2)]


if __name__ == "__main__":
    print("Pronunciation Trainer Module Loaded")
    print("This module is designed to be imported and used in app.py")
