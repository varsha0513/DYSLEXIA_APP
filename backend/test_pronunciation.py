#!/usr/bin/env python3
"""
Pronunciation Module Verification & Testing Script

This script tests all components of the pronunciation assistance module.
Run from the backend directory:
    python test_pronunciation.py
"""

import requests
import json
import wave
import numpy as np
import sys
from pathlib import Path


class PronunciationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result"""
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {name:<40} [{status}]")
        if details:
            print(f"   └─ {details}")
        self.test_results.append((name, status))
    
    def test_backend_connection(self):
        """Test 1: Backend connectivity"""
        self.print_header("TEST 1: Backend Connection")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test("Backend Health", "PASS", f"Status: {data['status']}")
                return True
            else:
                self.print_test("Backend Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except requests.ConnectionError as e:
            self.print_test("Backend Health", "FAIL", f"Connection error: {str(e)}")
            print("\n⚠️  Backend server not running!")
            print("   Start it with: python app.py")
            return False
        except Exception as e:
            self.print_test("Backend Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_tts_endpoint(self):
        """Test 2: TTS pronunciation generation"""
        self.print_header("TEST 2: Text-to-Speech (\"Hear It\" Button)")
        
        test_words = ["hello", "world", "pronunciation", "test"]
        
        for word in test_words:
            try:
                response = self.session.post(
                    f"{self.base_url}/pronunciation/word-audio",
                    data={"word": word},
                    timeout=15
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    if audio_size > 1000:  # Reasonable audio file size
                        self.print_test(
                            f"TTS for '{word}'",
                            "PASS",
                            f"Generated {audio_size} bytes of audio"
                        )
                    else:
                        self.print_test(
                            f"TTS for '{word}'",
                            "FAIL",
                            f"Audio too small: {audio_size} bytes"
                        )
                else:
                    self.print_test(
                        f"TTS for '{word}'",
                        "FAIL",
                        f"HTTP {response.status_code}"
                    )
            except Exception as e:
                self.print_test(
                    f"TTS for '{word}'",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def create_test_wav(self, filename: str = "test_audio.wav", duration: float = 1.0):
        """Create a test WAV file"""
        sample_rate = 16000
        frequency = 440  # Hz (A note)
        amplitude = 0.3
        
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = amplitude * np.sin(2 * np.pi * frequency * t)
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save WAV file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)      # Mono
            wav_file.setsampwidth(2)       # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return filename
    
    def test_word_comparison(self):
        """Test 3: Word comparison endpoint"""
        self.print_header("TEST 3: Word Comparison (Text-Only Analysis)")
        
        test_cases = [
            ("hello", "hello", "Exact match"),
            ("helo", "hello", "Minor typo"),
            ("world", "word", "Significant difference"),
            ("test", "testing", "Different length"),
            ("audio", "audio", "Exact match 2"),
        ]
        
        for spoken, target, description in test_cases:
            try:
                response = self.session.post(
                    f"{self.base_url}/pronunciation/word-comparison",
                    data={
                        "spoken_word": spoken,
                        "target_word": target
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    similarity = data.get("similarity_ratio", 0)
                    exact = data.get("is_exact_match", False)
                    
                    match_type = "✓ Exact" if exact else f"~{similarity*100:.0f}%"
                    self.print_test(
                        f"Compare '{spoken}' → '{target}'",
                        "PASS",
                        f"{description} | {match_type}"
                    )
                else:
                    self.print_test(
                        f"Compare '{spoken}' → '{target}'",
                        "FAIL",
                        f"HTTP {response.status_code}"
                    )
            except Exception as e:
                self.print_test(
                    f"Compare '{spoken}' → '{target}'",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def test_pronunciation_check(self):
        """Test 4: Full pronunciation check with audio"""
        self.print_header("TEST 4: Complete Pronunciation Check")
        
        print("📝 Creating test audio files...\n")
        
        test_words = ["hello", "world", "test"]
        
        for word in test_words:
            try:
                # Create test audio
                audio_file = self.create_test_wav(f"test_{word}.wav")
                
                # Send to backend
                with open(audio_file, 'rb') as f:
                    files = {'audio_file': f}
                    data = {'word': word}
                    
                    response = self.session.post(
                        f"{self.base_url}/pronunciation/check",
                        files=files,
                        data=data,
                        timeout=15
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    is_correct = result.get("is_correct", False)
                    similarity = result.get("similarity_ratio", 0)
                    recognized = result.get("recognized", "N/A")
                    
                    status = "✓ Correct" if is_correct else "✗ Needs retry"
                    self.print_test(
                        f"Check '{word}' pronunciation",
                        "PASS",
                        f"Recognized: '{recognized}' | {status} ({similarity*100:.0f}%)"
                    )
                    
                    # Check feedback
                    feedback = result.get("feedback", "")
                    if feedback:
                        print(f"   └─ Feedback: {feedback}")
                else:
                    self.print_test(
                        f"Check '{word}' pronunciation",
                        "FAIL",
                        f"HTTP {response.status_code}"
                    )
                
                # Clean up
                Path(audio_file).unlink(missing_ok=True)
                
            except Exception as e:
                self.print_test(
                    f"Check '{word}' pronunciation",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def test_batch_check(self):
        """Test 5: Batch word checking"""
        self.print_header("TEST 5: Batch Word Checking")
        
        words = ["pronunciation", "learning", "practice", "assistant"]
        
        try:
            response = self.session.post(
                f"{self.base_url}/pronunciation/batch-check",
                data={
                    "words": json.dumps(words)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_words", 0)
                
                self.print_test(
                    "Batch check initialization",
                    "PASS",
                    f"Prepared {total} words for practice"
                )
                
                words_list = data.get("words", [])
                for word_data in words_list:
                    word = word_data.get("word", "")
                    status = word_data.get("status", "")
                    print(f"   └─ {word}: {status}")
            else:
                self.print_test(
                    "Batch check initialization",
                    "FAIL",
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.print_test(
                "Batch check initialization",
                "FAIL",
                f"Error: {str(e)}"
            )
    
    def test_edge_cases(self):
        """Test 6: Edge cases and error handling"""
        self.print_header("TEST 6: Edge Cases & Error Handling")
        
        # Test 1: Empty word
        try:
            response = self.session.post(
                f"{self.base_url}/pronunciation/word-audio",
                data={"word": ""},
                timeout=5
            )
            
            if response.status_code == 400:
                self.print_test(
                    "Empty word handling",
                    "PASS",
                    "Correctly rejects empty word"
                )
            else:
                self.print_test(
                    "Empty word handling",
                    "FAIL",
                    f"Expected 400, got {response.status_code}"
                )
        except Exception as e:
            self.print_test(
                "Empty word handling",
                "FAIL",
                f"Error: {str(e)}"
            )
        
        # Test 2: Missing audio file
        try:
            response = self.session.post(
                f"{self.base_url}/pronunciation/check",
                data={"word": "test"},
                timeout=5
            )
            
            if response.status_code in [400, 422]:
                self.print_test(
                    "Missing audio file handling",
                    "PASS",
                    f"Correctly rejects request (HTTP {response.status_code})"
                )
            else:
                self.print_test(
                    "Missing audio file handling",
                    "FAIL",
                    f"Expected 400/422, got {response.status_code}"
                )
        except Exception as e:
            self.print_test(
                "Missing audio file handling",
                "FAIL",
                f"Error: {str(e)}"
            )
        
        # Test 3: Special characters
        try:
            response = self.session.post(
                f"{self.base_url}/pronunciation/word-comparison",
                data={
                    "spoken_word": "hello!@#",
                    "target_word": "hello"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.print_test(
                    "Special character handling",
                    "PASS",
                    "Correctly processes special characters"
                )
            else:
                self.print_test(
                    "Special character handling",
                    "FAIL",
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.print_test(
                "Special character handling",
                "FAIL",
                f"Error: {str(e)}"
            )
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.test_results)
        passed = sum(1 for _, status in self.test_results if status == "PASS")
        failed = total - passed
        
        print(f"Total Tests:  {total}")
        print(f"Passed:       {passed} ✅")
        print(f"Failed:       {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")
        
        if failed == 0:
            print("🎉 All tests passed! Pronunciation module is working correctly.\n")
        else:
            print(f"⚠️  {failed} test(s) failed. Check errors above.\n")
            
        return failed == 0
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("PRONUNCIATION MODULE VERIFICATION")
        print("Testing all components of the pronunciation training system...")
        
        # Test 1: Backend
        if not self.test_backend_connection():
            print("\n❌ Cannot continue - backend is not running")
            print("   Start the backend with: python app.py")
            return False
        
        # Test 2-6: Various features
        self.test_tts_endpoint()
        self.test_word_comparison()
        self.test_pronunciation_check()
        self.test_batch_check()
        self.test_edge_cases()
        
        # Summary
        return self.print_summary()


def main():
    """Main entry point"""
    tester = PronunciationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
