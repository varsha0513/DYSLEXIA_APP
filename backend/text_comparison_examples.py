"""
Text Comparison Examples & Test Cases
Demonstrates all features of the text comparison module
"""

from text_comparison import compare_text, get_performance_feedback


def example_1_basic_comparison():
    """Example 1: Basic word-by-word comparison"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Text Comparison")
    print("="*70)
    
    reference = "The quick brown fox jumps over the lazy dog"
    spoken = "The quick brown fox jumps over the dog"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_2_with_mistakes():
    """Example 2: Text with pronunciation mistakes"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Text with Pronunciation Mistakes")
    print("="*70)
    
    reference = "Beautiful butterflies flutter through the garden"
    spoken = "Beautiful butterfles flutter through the gardin"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_3_missing_words():
    """Example 3: Missing words in spoken text"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Missing Words (Student skipped some words)")
    print("="*70)
    
    reference = "She walked slowly to the store and bought some groceries"
    spoken = "She walked to store and bought groceries"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_4_extra_words():
    """Example 4: Extra words in spoken text"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Extra Words (Student added words)")
    print("="*70)
    
    reference = "The cat sat on the mat"
    spoken = "The little cat sat on the old mat"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_5_punctuation_handling():
    """Example 5: Punctuation is automatically handled"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Punctuation & Case Sensitivity (Auto-handled)")
    print("="*70)
    
    reference = "Hello! How are you today? I'm fine, thank you."
    spoken = "hello how are you today im fine thank you"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults (punctuation & case removed):")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_6_perfect_reading():
    """Example 6: Perfect reading accuracy"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Perfect Reading (100% Accuracy)")
    print("="*70)
    
    reference = "Good morning everyone"
    spoken = "Good morning everyone"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  Correct:        {result['correct_words']}")
    print(f"  Wrong:          {result['wrong_words']}")
    print(f"  Missing:        {result['missing_words']}")
    print(f"  Extra:          {result['extra_words']}")
    print(f"  Accuracy:       {result['accuracy_percent']}%")
    print(f"  Feedback:       {get_performance_feedback(result['accuracy_percent'])}")


def example_7_feedback_levels():
    """Example 7: All feedback levels"""
    print("\n" + "="*70)
    print("EXAMPLE 7: All Feedback Levels")
    print("="*70)
    
    accuracy_list = [95, 85, 75, 65, 50]
    
    for acc in accuracy_list:
        feedback = get_performance_feedback(acc)
        print(f"Accuracy {acc:3d}%: {feedback}")


def example_8_realistic_student_scenario():
    """Example 8: Realistic student reading scenario"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Realistic Student Reading (Multiple Errors)")
    print("="*70)
    
    reference = "The ancient library contained thousands of precious books and manuscripts from many different cultures and time periods"
    spoken = "The ancient library contained thousands of precious books and manuscripts from different cultures"
    
    print(f"Reference: {reference}")
    print(f"Spoken:    {spoken}")
    print(f"\nNote: Student struggled with 'many' and skipped 'time periods'")
    
    result = compare_text(reference, spoken)
    
    print(f"\nResults:")
    print(f"  Total Words:    {result['total_words']}")
    print(f"  ✅ Correct:     {result['correct_words']} words read correctly")
    print(f"  ❌ Wrong:       {result['wrong_words']} words read incorrectly")
    print(f"  ⚠ Missing:      {result['missing_words']} words were skipped")
    print(f"  ➕ Extra:        {result['extra_words']} extra words added")
    print(f"  📈 Accuracy:    {result['accuracy_percent']}%\n")
    print(f"  💡 Feedback:    {get_performance_feedback(result['accuracy_percent'])}")
    print(f"\n  📊 Analysis: The student needs to practice the phrases:")
    print(f"     - 'many different' (struggled with sequence)")
    print(f"     - 'time periods' (skipped at end)")


def run_all_examples():
    """Run all examples"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DYSLEXIA APP - TEXT COMPARISON EXAMPLES & TESTS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    example_1_basic_comparison()
    example_2_with_mistakes()
    example_3_missing_words()
    example_4_extra_words()
    example_5_punctuation_handling()
    example_6_perfect_reading()
    example_7_feedback_levels()
    example_8_realistic_student_scenario()
    
    print("\n" + "█"*70)
    print("█" + "  ALL EXAMPLES COMPLETE ✅".center(68) + "█")
    print("█"*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
