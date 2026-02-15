import sounddevice as sd
import queue
import json
import os
from vosk import Model, KaldiRecognizer
from text_comparison import compare_text, get_performance_feedback

# Load model
model_path = "../model/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    print("Please download the model first")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))


def run_reading_test(reference_text):
    """
    Run a reading test with Vosk speech recognition and text comparison.
    
    Args:
        reference_text (str): The paragraph the user should read
    
    Returns:
        dict: Contains recognition results and accuracy metrics
    """
    print(f"\n📖 Please read the following text:")
    print(f"   \"{reference_text}\"")
    print("\n🎤 Start reading... Press Ctrl+C to stop\n")
    
    recognized_text = ""
    
    try:
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
                        print(f"✅ Recognized: {recognized_text}\n")
                        
                        # Compare texts and get results
                        comparison_result = compare_text(reference_text, recognized_text)
                        
                        # Display results
                        print("="*60)
                        print("📊 READING PERFORMANCE REPORT")
                        print("="*60)
                        print(f"Reference Text: {reference_text}")
                        print(f"Recognized:    {recognized_text}")
                        print("-"*60)
                        print(f"Total Words:        {comparison_result['total_words']}")
                        print(f"✅ Correct Words:    {comparison_result['correct_words']}")
                        print(f"❌ Wrong Words:      {comparison_result['wrong_words']}")
                        print(f"⚠ Missing Words:     {comparison_result['missing_words']}")
                        print(f"➕ Extra Words:       {comparison_result['extra_words']}")
                        print(f"📈 Accuracy:         {comparison_result['accuracy_percent']}%")
                        print("-"*60)
                        feedback = get_performance_feedback(comparison_result['accuracy_percent'])
                        print(f"💡 {feedback}")
                        print("="*60 + "\n")
                        
                        return {
                            "reference_text": reference_text,
                            "recognized_text": recognized_text,
                            "comparison_result": comparison_result,
                            "feedback": feedback
                        }
                    
    except KeyboardInterrupt:
        print("\n⏹ Recording stopped by user")
        if recognized_text:
            comparison_result = compare_text(reference_text, recognized_text)
            feedback = get_performance_feedback(comparison_result['accuracy_percent'])
            return {
                "reference_text": reference_text,
                "recognized_text": recognized_text,
                "comparison_result": comparison_result,
                "feedback": feedback
            }
        return None


if __name__ == "__main__":
    # Example reading passages
    passages = [
        "The quick brown fox jumps over the lazy dog.",
        "Reading is a wonderful way to learn new things.",
        "Practice makes perfect when learning to read."
    ]
    
    print("\n🎯 DYSLEXIA APP - READING ASSESSMENT TOOL")
    print("="*60)
    
    # Start with first passage as example
    result = run_reading_test(passages[0])
    
    if result:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n⏹ Test cancelled - no recognized text")
