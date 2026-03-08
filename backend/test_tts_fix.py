#!/usr/bin/env python
"""Test the TTS fix for multiple concurrent requests"""

from text_to_speech import DyslexiaAssistanceEngine
import time

print("=" * 60)
print("Testing TTS Engine Fix")
print("=" * 60)

engine = DyslexiaAssistanceEngine()

# Test 3 consecutive requests
words = ['hello', 'world', 'test']

for i, word in enumerate(words, 1):
    print(f"\nRequest {i}: Generating audio for '{word}'...")
    start = time.time()
    try:
        audio_bytes, _ = engine.generate_audio_file(word)
        elapsed = time.time() - start
        if audio_bytes:
            print(f"  ✅ Success in {elapsed:.2f}s - {len(audio_bytes)} bytes")
        else:
            print(f"  ❌ Failed - no audio data returned")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ Error in {elapsed:.2f}s: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
