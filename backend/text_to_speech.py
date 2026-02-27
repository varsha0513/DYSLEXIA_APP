"""
Text-to-Speech (TTS) Module for Dyslexia Assistance
Uses pyttsx3 for offline, reliable pronunciation guidance
"""

import pyttsx3
import io
import base64
from typing import Dict, List, Tuple
import json


class DyslexiaAssistanceEngine:
    """
    Provides pronunciation assistance for incorrect words
    Generates audio files for corrected words and detailed feedback
    """
    
    def __init__(self, rate: int = 100, volume: float = 0.9):
        """
        Initialize TTS engine
        
        Args:
            rate: Speech rate (100 = normal, 50-300 available)
            volume: Volume level (0.0-1.0)
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            print("✅ TTS Engine initialized successfully")
        except Exception as e:
            print(f"⚠️ Could not initialize TTS engine: {e}")
            self.engine = None
    
    def generate_audio_file(self, text: str) -> Tuple[bytes, str]:
        """
        Generate audio bytes for given text
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Tuple of (audio_bytes, audio_base64) for transmission
        """
        if not self.engine:
            print("❌ TTS Engine not available")
            return b'', ''
        
        try:
            # Use BytesIO to capture audio to memory
            audio_buffer = io.BytesIO()
            
            self.engine.save_to_file(text, 'temp_audio.wav')
            self.engine.runAndWait()
            
            # Read the generated WAV file
            with open('temp_audio.wav', 'rb') as f:
                audio_bytes = f.read()
            
            # Convert to base64 for transmission
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            print(f"✅ Generated audio for '{text}' ({len(audio_bytes)} bytes)")
            return audio_bytes, audio_base64
            
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            return b'', ''
    
    def generate_word_assistance(self, wrong_word: str, correct_word: str) -> Dict:
        """
        Generate complete assistance for a misread word
        
        Args:
            wrong_word: What the user said
            correct_word: What should have been said
            
        Returns:
            Dictionary with pronunciation guide and audio
        """
        if not self.engine:
            return {
                "wrong_word": wrong_word,
                "correct_word": correct_word,
                "audio_base64": "",
                "message": "TTS unavailable",
                "status": "error"
            }
        
        try:
            # Generate correct pronunciation audio
            _, audio_base64 = self.generate_audio_file(correct_word)
            
            return {
                "wrong_word": wrong_word,
                "correct_word": correct_word,
                "audio_base64": audio_base64,
                "audio_url": f"data:audio/wav;base64,{audio_base64}",
                "message": f"You said '{wrong_word}' instead of '{correct_word}'. Listen to the correct pronunciation above.",
                "status": "success"
            }
        
        except Exception as e:
            print(f"❌ Error in word assistance: {e}")
            return {
                "wrong_word": wrong_word,
                "correct_word": correct_word,
                "audio_base64": "",
                "error": str(e),
                "status": "error"
            }
    
    def generate_missing_word_assistance(self, missing_word: str) -> Dict:
        """
        Generate assistance for a missing word
        
        Args:
            missing_word: Word that was skipped
            
        Returns:
            Dictionary with pronunciation guide for the missing word
        """
        if not self.engine:
            return {
                "missing_word": missing_word,
                "audio_base64": "",
                "message": "TTS unavailable",
                "status": "error"
            }
        
        try:
            _, audio_base64 = self.generate_audio_file(missing_word)
            
            return {
                "missing_word": missing_word,
                "audio_base64": audio_base64,
                "audio_url": f"data:audio/wav;base64,{audio_base64}",
                "message": f"You skipped this word. Listen: '{missing_word}'. Try reading it again.",
                "status": "success"
            }
        
        except Exception as e:
            print(f"❌ Error in missing word assistance: {e}")
            return {
                "missing_word": missing_word,
                "audio_base64": "",
                "error": str(e),
                "status": "error"
            }
    
    def generate_complete_assistance(self, paragraph: str, wrong_words_list: List[Tuple[str, str]], 
                                    missing_words_list: List[str]) -> Dict:
        """
        Generate complete assistance for all errors in a paragraph
        
        Args:
            paragraph: Original paragraph
            wrong_words_list: List of (wrong, correct) tuples
            missing_words_list: List of missing words
            
        Returns:
            Dictionary with all assistance data organized by error type
        """
        assistance = {
            "paragraph": paragraph,
            "word_errors": [],
            "missing_words": [],
            "practice_plan": None,
            "status": "success" if self.engine else "warning"
        }
        
        # Generate word error assistance
        for wrong, correct in wrong_words_list:
            assistance["word_errors"].append(
                self.generate_word_assistance(wrong, correct)
            )
        
        # Generate missing word assistance
        for missing in missing_words_list:
            assistance["missing_words"].append(
                self.generate_missing_word_assistance(missing)
            )
        
        # Create practice plan
        total_errors = len(wrong_words_list) + len(missing_words_list)
        if total_errors > 0:
            assistance["practice_plan"] = {
                "total_errors": total_errors,
                "instructions": [
                    "👂 Listen to each correct pronunciation",
                    "🔄 Click the Repeat button to hear it again",
                    "📖 Read the paragraph once more slowly",
                    "🎯 Focus on the words you struggled with"
                ],
                "motivation": "Great job taking the assessment! These corrections will help you improve. Practice makes perfect!"
            }
        
        return assistance


def create_assistance_response(comparison_result: dict, paragraph: str) -> Dict:
    """
    Helper function to create complete assistance response
    
    Args:
        comparison_result: From compare_text()
        paragraph: Original paragraph
        
    Returns:
        Complete assistance dictionary
    """
    engine = DyslexiaAssistanceEngine()
    
    # Extract error words (simplified - would need enhanced compare_text)
    # For now, returning basic assistance
    assistance = {
        "has_errors": comparison_result['wrong_words'] > 0 or comparison_result['missing_words'] > 0,
        "error_count": comparison_result['wrong_words'] + comparison_result['missing_words'],
        "word_errors": [],
        "missing_words": [],
        "assistance_enabled": engine.engine is not None,
        "status": "success" if engine.engine else "tts_unavailable"
    }
    
    return assistance


if __name__ == "__main__":
    # Test the TTS engine
    print("\n" + "="*70)
    print("🧪 TESTING TEXT-TO-SPEECH ASSISTANCE")
    print("="*70 + "\n")
    
    engine = DyslexiaAssistanceEngine()
    
    # Test 1: Generate simple word assistance
    print("Test 1: Word Error Assistance")
    result = engine.generate_word_assistance("park", "park")
    print(f"Result: {json.dumps(result, indent=2)[:200]}...\n")
    
    # Test 2: Generate missing word assistance
    print("Test 2: Missing Word Assistance")
    result = engine.generate_missing_word_assistance("important")
    print(f"Result: {json.dumps(result, indent=2)[:200]}...\n")
    
    print("✅ TTS Module tests complete!")
    print("="*70)
