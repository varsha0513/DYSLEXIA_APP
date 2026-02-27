import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


def clean_text(text):
    """
    Clean and normalize text for comparison.
    - Convert to lowercase
    - Remove punctuation
    - Remove extra whitespace
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_word_level_errors(reference_text: str, spoken_text: str) -> Dict:
    """
    Get detailed word-level error information for assistance
    
    Args:
        reference_text (str): The original paragraph to be read
        spoken_text (str): The text recognized by Vosk
    
    Returns:
        dict: Contains:
            - wrong_words: List of (spoken, correct) tuples
            - missing_words: List of words that were skipped
            - extra_words: List of extra words spoken
    """
    ref = clean_text(reference_text).split()
    spoken = clean_text(spoken_text).split()
    
    matcher = SequenceMatcher(None, ref, spoken)
    
    wrong_words = []
    missing_words = []
    extra_words = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            # Words that were said incorrectly
            for k in range(max(i2 - i1, j2 - j1)):
                wrong = spoken[j1 + k] if j1 + k < j2 else "[missing]"
                correct = ref[i1 + k] if i1 + k < i2 else "[extra]"
                if wrong != "[missing]" and correct != "[extra]":
                    wrong_words.append((wrong, correct))
        elif tag == "delete":
            # Words that were skipped
            missing_words.extend(ref[i1:i2])
        elif tag == "insert":
            # Extra words that were added
            extra_words.extend(spoken[j1:j2])
    
    return {
        "wrong_words": wrong_words,
        "missing_words": missing_words,
        "extra_words": extra_words
    }


def compare_text(reference_text, spoken_text):
    """
    Compare reference text with spoken text from Vosk.
    
    Args:
        reference_text (str): The original paragraph to be read
        spoken_text (str): The text recognized by Vosk
    
    Returns:
        dict: Contains accuracy metrics:
            - total_words: Total words in reference text
            - correct_words: Words that matched
            - wrong_words: Words that were incorrect
            - missing_words: Words that were skipped
            - extra_words: Additional words spoken
            - accuracy_percent: Accuracy as percentage
            - word_level_errors: Detailed error information
    """
    ref = clean_text(reference_text).split()
    spoken = clean_text(spoken_text).split()

    matcher = SequenceMatcher(None, ref, spoken)

    correct = 0
    wrong = 0
    missing = 0
    extra = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            correct += (i2 - i1)
        elif tag == "replace":
            wrong += max(i2 - i1, j2 - j1)
        elif tag == "delete":
            missing += (i2 - i1)
        elif tag == "insert":
            extra += (j2 - j1)

    total_ref_words = len(ref)
    accuracy = (correct / total_ref_words) * 100 if total_ref_words > 0 else 0
    
    # Get word-level error details
    word_errors = get_word_level_errors(reference_text, spoken_text)

    return {
        "total_words": total_ref_words,
        "correct_words": correct,
        "wrong_words": wrong,
        "missing_words": missing,
        "extra_words": extra,
        "accuracy_percent": round(accuracy, 2),
        "word_level_errors": word_errors
    }


def get_performance_feedback(accuracy_percent):
    """
    Generate performance feedback based on accuracy percentage.
    
    Args:
        accuracy_percent (float): Accuracy percentage (0-100)
    
    Returns:
        str: Feedback message
    """
    if accuracy_percent >= 90:
        return "🌟 Excellent reading! Keep it up!"
    elif accuracy_percent >= 80:
        return "👍 Good job! Just a few words to work on."
    elif accuracy_percent >= 70:
        return "📚 Nice effort! Practice a bit more."
    elif accuracy_percent >= 60:
        return "💪 Keep practicing! You're making progress."
    else:
        return "📖 Let's practice this passage again!"


if __name__ == "__main__":
    # Example usage
    reference_text = "The boy is playing in the park with his friends."
    spoken_text = "The boy is playing in park with friends"
    
    result = compare_text(reference_text, spoken_text)
    
    print("\n" + "="*60)
    print("📊 TEXT COMPARISON RESULTS")
    print("="*60)
    print(f"Reference: {reference_text}")
    print(f"Spoken:    {spoken_text}")
    print("-"*60)
    print(f"Total Words:        {result['total_words']}")
    print(f"✅ Correct Words:    {result['correct_words']}")
    print(f"❌ Wrong Words:      {result['wrong_words']}")
    print(f"⚠ Missing Words:     {result['missing_words']}")
    print(f"➕ Extra Words:       {result['extra_words']}")
    print(f"📈 Accuracy:         {result['accuracy_percent']}%")
    print("-"*60)
    print(f"Feedback: {get_performance_feedback(result['accuracy_percent'])}")
    print("="*60 + "\n")
