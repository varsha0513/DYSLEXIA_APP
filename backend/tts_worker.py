#!/usr/bin/env python
"""
Isolated TTS Worker Process
Runs in a subprocess to avoid pyttsx3 singleton/threading issues
"""

import sys
import pyttsx3
import os

def generate_tts(text: str, output_path: str) -> bool:
    """
    Generate TTS audio in isolation
    
    Args:
        text: Text to synthesize
        output_path: Where to save the WAV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 100)
        engine.setProperty('volume', 0.9)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        # Verify file was created
        if os.path.exists(output_path):
            return True
        else:
            print(f"ERROR: Output file not created: {output_path}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: tts_worker.py <text> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    text = sys.argv[1]
    output_path = sys.argv[2]
    
    success = generate_tts(text, output_path)
    sys.exit(0 if success else 1)
