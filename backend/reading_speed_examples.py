"""
Reading Speed (WPM) Analysis Examples
Demonstrates the dyslexia indicators through reading speed
"""

from reading_speed import ReadingSpeedAnalyzer, analyze_reading_session


def example_1_normal_reader():
    """Example 1: Student with normal reading speed"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Normal Reader (Typical age-appropriate speed)")
    print("="*70)
    
    reference = "The quick brown fox jumps over the lazy dog"
    spoken = "The quick brown fox jumps over the lazy dog"
    elapsed_time = 25  # seconds
    
    print(f"Passage: {reference}")
    print(f"Spoken:  {spoken}")
    print(f"\nTime to read: {elapsed_time} seconds")
    
    result = analyze_reading_session(reference, spoken, elapsed_time)
    
    print(f"\nResults:")
    print(f"  Words Spoken: {result['spoken_words']}")
    print(f"  WPM: {result['wpm']}")
    print(f"  Category: {result['speed_category']} {result['speed_indicator']}")
    print(f"  Dyslexia Risk (Speed): {result['dyslexia_risk_wpm']}")


def example_2_slow_reader():
    """Example 2: Student with slower reading speed (possible dyslexia)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Slow Reader (Potential dyslexia indicator)")
    print("="*70)
    
    reference = "The quick brown fox jumps over the lazy dog"
    spoken = "The quick brown fox jumps over the lazy dog"
    elapsed_time = 45  # Takes much longer
    
    print(f"Passage: {reference}")
    print(f"Spoken:  {spoken}")
    print(f"\nTime to read: {elapsed_time} seconds (Much slower)")
    
    result = analyze_reading_session(reference, spoken, elapsed_time)
    
    print(f"\nResults:")
    print(f"  Words Spoken: {result['spoken_words']}")
    print(f"  WPM: {result['wpm']}")
    print(f"  Category: {result['speed_category']} {result['speed_indicator']}")
    print(f"  Dyslexia Risk (Speed): {result['dyslexia_risk_wpm']}")
    print(f"\n⚠️ Analysis: This is a STRONG dyslexia indicator")


def example_3_very_slow_reader():
    """Example 3: Very slow reader (strong dyslexia indicator)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Very Slow Reader (Strong dyslexia indicator)")
    print("="*70)
    
    reference = "The boy is playing in the park with his friends"
    spoken = "The boy is playing in the park with his friends"
    elapsed_time = 60  # 1 full minute for short passage
    
    print(f"Passage: {reference}")
    print(f"Spoken:  {spoken}")
    print(f"\nTime to read: {elapsed_time} seconds (1 minute for short passage!)")
    
    result = analyze_reading_session(reference, spoken, elapsed_time)
    
    print(f"\nResults:")
    print(f"  Words Spoken: {result['spoken_words']}")
    print(f"  WPM: {result['wpm']}")
    print(f"  Category: {result['speed_category']} {result['speed_indicator']}")
    print(f"  Dyslexia Risk (Speed): {result['dyslexia_risk_wpm']}")
    print(f"\n🚩 Analysis: STRONG dyslexia indicator - immediate intervention needed")


def example_4_wpm_standards():
    """Example 4: Grade-level WPM standards"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Grade-Level WPM Standards")
    print("="*70)
    print("""
Expected WPM by Grade Level (Normal Reading Progression):
    Grade 1:    20-30 WPM
    Grade 2:    30-50 WPM
    Grade 3:    60-90 WPM
    Grade 4:    90-120 WPM
    Grade 5:    110-140 WPM
    Grade 6:    120-150 WPM
    Grade 7+:   150+ WPM
    Adult:      200-300 WPM
    """)
    
    analyzer = ReadingSpeedAnalyzer()
    
    test_cases = [
        ("Grade 3 Expected", 75),
        ("Grade 3 Below Average", 50),
        ("Grade 3 Possible Dyslexia", 35),
        ("Grade 5 Expected", 125),
        ("Grade 5 Below Average", 80),
    ]
    
    print("Assessment Examples:\n")
    for name, wpm in test_cases:
        category = analyzer.get_reading_speed_category(wpm)
        status = f"✅ On track" if wpm >= 75 else f"⚠️ Below expected"
        print(f"  {name:30s} ({wpm:3d} WPM): {status}")
        print(f"    └─ {category['indicator']}\n")


def example_5_combined_speed_accuracy():
    """Example 5: Combining speed and accuracy for diagnosis"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Combined Speed + Accuracy for Diagnosis")
    print("="*70)
    print("""
4x4 Diagnostic Matrix:
    
    Speed →
Accuracy↓   Fast (150+ WPM) | Moderate (100-149) | Slow (60-99) | Very Slow (<60)
─────────────────────────────────────────────────────────────────────────────
High (90%+) |  Excellent      |  Good              |  Possible     |  Strong
            |  Advanced level | Normal level       |  anxiety      |  indicator
─────────────────────────────────────────────────────────────────────────────
Good (80%) |  Good           |  Good              |  Practice     |  Possible
           |  Normal         |  Normal            |  needed       |  indicator
─────────────────────────────────────────────────────────────────────────────
Fair (70%) |  Fair           |  Fair              |  Needs        |  Likely
           |  May need work  |  Needs practice    |  intervention |  dyslexia
─────────────────────────────────────────────────────────────────────────────
Low (<70%) |  Struggling     |  Struggling        |  High risk    |  Very high
           |  Possible issue |  Higher risk       |  dyslexia     |  risk
    """)
    
    # Real case examples
    print("\nExample Cases:\n")
    
    cases = [
        {
            "name": "Student A: Normal Reader",
            "accuracy": 92,
            "wpm": 125,
            "diagnosis": "✅ No dyslexia indicators"
        },
        {
            "name": "Student B: Fast but careless",
            "accuracy": 82,
            "wpm": 160,
            "diagnosis": "⚠️ May need to slow down for comprehension"
        },
        {
            "name": "Student C: Slow and struggling",
            "accuracy": 68,
            "wpm": 65,
            "diagnosis": "🚩 Strong dyslexia indicators - needs assessment"
        },
        {
            "name": "Student D: Accurate but slow",
            "accuracy": 88,
            "wpm": 70,
            "diagnosis": "⚠️ Possible reading anxiety or processing issue"
        },
    ]
    
    for case in cases:
        print(f"  {case['name']}")
        print(f"    Accuracy: {case['accuracy']}%, WPM: {case['wpm']}")
        print(f"    → {case['diagnosis']}\n")


def example_6_with_pauses():
    """Example 6: Impact of pauses on reading speed"""
    print("\n" + "="*70)
    print("EXAMPLE 6: How Pauses Affect WPM (Important for Dyslexia)")
    print("="*70)
    
    print("\nSame passage, different patterns:\n")
    
    cases = [
        {
            "reading_pattern": "Smooth, continuous reading",
            "words": 50,
            "time": 30,
            "note": "Fluent reader"
        },
        {
            "reading_pattern": "Multiple pauses to decode words",
            "words": 50,
            "time": 45,
            "note": "Struggling with word recognition"
        },
        {
            "reading_pattern": "Long pauses, hesitations",
            "words": 50,
            "time": 60,
            "note": "DYSLEXIA INDICATOR: Significant decoding difficulty"
        },
        {
            "reading_pattern": "Very long pauses between phrases",
            "words": 50,
            "time": 90,
            "note": "STRONG DYSLEXIA INDICATOR: Severe decoding issues"
        },
    ]
    
    for case in cases:
        wpm = (case['words'] / case['time']) * 60
        print(f"  Pattern: {case['reading_pattern']}")
        print(f"  Time: {case['time']}s for {case['words']} words")
        print(f"  WPM: {wpm:.1f}")
        print(f"  Interpretation: {case['note']}\n")


def example_7_real_student_scenario():
    """Example 7: Real student scenario with multiple factors"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Real Student Scenario (Multiple Dyslexia Factors)")
    print("="*70)
    
    print("\nStudent Profile: Mason, Grade 4 (Age 9)")
    print("-" * 70)
    
    # Multiple passages to show pattern
    passages = [
        ("Passage 1", "The cat sat on the mat", 35, "cat sat mat"),
        ("Passage 2", "I like to read books in the park", 55, "I like read books park"),
        ("Passage 3", "She walked quickly up the stairs", 50, "She walked quick the stairs"),
    ]
    
    analyzer = ReadingSpeedAnalyzer()
    
    print("\nAssessment Results:\n")
    total_wpm = 0
    
    for passage_num, reference, time_taken, recognized in passages:
        words_spoken = len(recognized.split())
        wpm = (words_spoken / time_taken) * 60
        total_wpm += wpm
        
        speed_cat = analyzer.get_reading_speed_category(wpm)
        
        print(f"  {passage_num}:")
        print(f"    Time: {time_taken}s, Words: {words_spoken}, WPM: {wpm:.1f}")
        print(f"    Speed Category: {speed_cat['category']}")
        print(f"    Risk Level: {speed_cat['dyslexia_risk']}\n")
    
    avg_wpm = total_wpm / len(passages)
    overall_cat = analyzer.get_reading_speed_category(avg_wpm)
    
    print(f"Average WPM across all passages: {avg_wpm:.1f}")
    print(f"Expected for Grade 4: 90-120 WPM")
    print(f"\n🔍 Diagnostic Summary:")
    print(f"  • Consistent slow reading ({avg_wpm:.1f} WPM vs expected 90-120)")
    print(f"  • Frequent word errors (saying 'quick' instead of 'quickly')")
    print(f"  • Word omissions ('the' skipped in passage 3)")
    print(f"\n  RECOMMENDATION: Strong dyslexia indicators")
    print(f"  ACTION: Refer for formal dyslexia assessment")


def example_8_progress_tracking():
    """Example 8: Tracking improvement over time"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Progress Tracking (Weekly Improvement)")
    print("="*70)
    
    # Simulate 4 weeks of reading practice
    weeks_data = [
        ("Week 1 (Baseline)", 45, 65),
        ("Week 2 (After intervention)", 52, 72),
        ("Week 3 (Continued practice)", 58, 78),
        ("Week 4 (Sustained improvement)", 65, 83),
    ]
    
    analyzer = ReadingSpeedAnalyzer()
    
    print("\nStudent: Alex (Dyslexia baseline)\n")
    print("Week          WPM    Accuracy    Progress        Status")
    print("-" * 70)
    
    baseline_wpm = weeks_data[0][1]
    baseline_acc = weeks_data[0][2]
    
    for week, wpm, accuracy in weeks_data:
        wpm_change = ((wpm - baseline_wpm) / baseline_wpm) * 100
        acc_change = accuracy - baseline_acc
        
        status_cat = analyzer.get_reading_speed_category(wpm)
        
        progress_indicator = "↑" if wpm > baseline_wpm else "="
        
        print(f"{week:20s} {wpm:3d}  {accuracy:2d}%     {wpm_change:+5.1f}%   {progress_indicator} {status_cat['category']}")
    
    print("\n✅ Analysis:")
    print("  • Consistent week-over-week improvement")
    print("  • Progressing from 'Very Slow' → 'Slow' category")
    print("  • Accuracy improving alongside speed (comprehensive improvement)")
    print("  • Intervention is working - continue current approach")


def run_all_examples():
    """Run all examples"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  READING SPEED (WPM) ANALYSIS - DYSLEXIA INDICATORS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    example_1_normal_reader()
    example_2_slow_reader()
    example_3_very_slow_reader()
    example_4_wpm_standards()
    example_5_combined_speed_accuracy()
    example_6_with_pauses()
    example_7_real_student_scenario()
    example_8_progress_tracking()
    
    print("\n" + "█"*70)
    print("█" + "  ALL EXAMPLES COMPLETE ✅".center(68) + "█")
    print("█"*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
