import sounddevice as sd
import queue
import json
import os
import time
from vosk import Model, KaldiRecognizer
from text_comparison import compare_text, get_performance_feedback
from reading_speed import ReadingSpeedAnalyzer

# Load model
model_path = "../model/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    print("Please download the model first")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))


def run_complete_reading_assessment(reference_text):
    """
    Run a complete reading assessment with:
    1. Text accuracy analysis (comparison)
    2. Reading speed analysis (WPM)
    3. Combined performance report
    
    Args:
        reference_text (str): The paragraph the user should read
    
    Returns:
        dict: Complete assessment including accuracy, speed, and feedback
    """
    print(f"\n{'='*70}")
    print("📖 READING ASSESSMENT - WITH SPEED & ACCURACY")
    print(f"{'='*70}")
    print(f"\n📖 Please read the following text:\n")
    print(f"   \"{reference_text}\"\n")
    print("🎤 Start reading... Press Ctrl+C to stop recording\n")
    
    # Initialize analyzer
    speed_analyzer = ReadingSpeedAnalyzer()
    recognized_text = ""
    
    try:
        # Start timer
        speed_analyzer.start_timer()
        
        with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=callback):
            
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    recognized_text = result.get("text", "")
                    
                    if recognized_text:
                        # Stop timer
                        speed_analyzer.stop_timer()
                        elapsed_time = speed_analyzer.get_elapsed_time()
                        
                        print(f"\n✅ Recognized: {recognized_text}\n")
                        
                        # Compare texts for accuracy
                        comparison_result = compare_text(reference_text, recognized_text)
                        
                        # Calculate WPM
                        spoken_words = len(recognized_text.split())
                        wpm = speed_analyzer.calculate_wpm(spoken_words)
                        speed_category = speed_analyzer.get_reading_speed_category(wpm)
                        
                        # Display comprehensive results
                        print("="*70)
                        print("📊 COMPLETE READING ASSESSMENT REPORT")
                        print("="*70)
                        
                        print(f"\nReference Text: {reference_text}")
                        print(f"Recognized:    {recognized_text}")
                        
                        print("\n" + "-"*70)
                        print("⏱️  READING SPEED METRICS")
                        print("-"*70)
                        print(f"Total Time:         {speed_analyzer.get_elapsed_time_formatted()}")
                        print(f"Total Words Spoken: {spoken_words}")
                        print(f"WPM (Words/Min):    {wpm}")
                        print(f"Speed Category:     {speed_category['category']}")
                        print(f"Status:             {speed_category['indicator']}")
                        print(f"Dyslexia Risk:      {speed_category['dyslexia_risk']}")
                        
                        print("\n" + "-"*70)
                        print("📈 READING ACCURACY METRICS")
                        print("-"*70)
                        print(f"Total Words (Reference): {comparison_result['total_words']}")
                        print(f"✅ Correct Words:        {comparison_result['correct_words']}")
                        print(f"❌ Wrong Words:          {comparison_result['wrong_words']}")
                        print(f"⚠ Missing Words:         {comparison_result['missing_words']}")
                        print(f"➕ Extra Words:           {comparison_result['extra_words']}")
                        print(f"📊 Accuracy:             {comparison_result['accuracy_percent']}%")
                        
                        # Get feedback
                        accuracy_feedback = get_performance_feedback(comparison_result['accuracy_percent'])
                        
                        print("\n" + "-"*70)
                        print("💡 COMBINED FEEDBACK & ASSESSMENT")
                        print("-"*70)
                        print(f"Accuracy Feedback:  {accuracy_feedback}")
                        
                        # Difficulty estimate
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
                        
                        print(f"Difficulty Level:   {difficulty}")
                        
                        # Dyslexia indicators
                        print("\n" + "-"*70)
                        print("🔍 DYSLEXIA INDICATORS")
                        print("-"*70)
                        
                        indicators = []
                        
                        if comparison_result['accuracy_percent'] < 70:
                            indicators.append("❌ Low accuracy (< 70%)")
                        
                        if wpm < 90:
                            indicators.append("⚠️ Slow reading speed (< 90 WPM)")
                        
                        if comparison_result['missing_words'] > 2:
                            indicators.append("⚠️ Frequent word omissions")
                        
                        if comparison_result['wrong_words'] > 2:
                            indicators.append("⚠️ Multiple pronunciation errors")
                        
                        if indicators:
                            risk_level = "High" if len(indicators) >= 2 else "Medium"
                            print(f"\nRisk Level: {risk_level}")
                            for indicator in indicators:
                                print(f"  {indicator}")
                        else:
                            print("\n✅ No major dyslexia indicators detected!")
                            print("   Student shows good reading ability")
                        
                        print("="*70 + "\n")
                        
                        return {
                            "reference_text": reference_text,
                            "recognized_text": recognized_text,
                            "speed_metrics": {
                                "elapsed_time_seconds": elapsed_time,
                                "elapsed_time_formatted": speed_analyzer.get_elapsed_time_formatted(),
                                "spoken_words": spoken_words,
                                "wpm": wpm,
                                "speed_category": speed_category['category'],
                                "speed_indicator": speed_category['indicator'],
                                "dyslexia_risk": speed_category['dyslexia_risk']
                            },
                            "accuracy_metrics": comparison_result,
                            "accuracy_feedback": accuracy_feedback,
                            "difficulty_assessment": difficulty,
                            "indicators": indicators if indicators else ["No concerns"]
                        }
    
    except KeyboardInterrupt:
        print("\n⏹ Recording stopped by user")
        if recognized_text:
            speed_analyzer.stop_timer()
            elapsed_time = speed_analyzer.get_elapsed_time()
            
            comparison_result = compare_text(reference_text, recognized_text)
            spoken_words = len(recognized_text.split())
            wpm = speed_analyzer.calculate_wpm(spoken_words)
            
            print(f"\n✅ Partial Results:")
            print(f"   Time: {speed_analyzer.get_elapsed_time_formatted()}")
            print(f"   WPM: {wpm}")
            print(f"   Accuracy: {comparison_result['accuracy_percent']}%\n")
            
            return {
                "reference_text": reference_text,
                "recognized_text": recognized_text,
                "speed_metrics": {
                    "elapsed_time_seconds": elapsed_time,
                    "wpm": wpm
                },
                "accuracy_metrics": comparison_result,
                "status": "User interrupted"
            }
        return None


if __name__ == "__main__":
    # Example reading passages (difficulty levels)
    passages = {
        "beginner": "The cat sat on the mat.",
        "intermediate": "The quick brown fox jumps over the lazy dog.",
        "advanced": "Reading requires focus and practice to develop strong comprehension and fluency skills."
    }
    
    print("\n🎯 DYSLEXIA APP - COMPLETE READING ASSESSMENT TOOL")
    print("="*70)
    print("This system measures BOTH speed (WPM) and accuracy")
    print("to identify dyslexia indicators")
    print("="*70)
    
    # Run beginner level assessment
    print("\nStarting with intermediate difficulty passage...")
    result = run_complete_reading_assessment(passages["intermediate"])
    
    if result:
        print(f"\n✅ Assessment completed successfully!")
        print(f"Results saved and ready for analysis")
    else:
        print(f"\n⏹ Assessment cancelled")
