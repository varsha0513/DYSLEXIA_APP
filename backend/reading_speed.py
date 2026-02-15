import time
from datetime import timedelta


class ReadingSpeedAnalyzer:
    """
    Analyzes reading speed (WPM) and time metrics for reading assessments.
    Critical for identifying dyslexia indicators like slow reading and hesitation.
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.pauses = []
        self.current_pause_start = None
    
    def start_timer(self):
        """Start the reading timer."""
        self.start_time = time.time()
        return self.start_time
    
    def stop_timer(self):
        """Stop the reading timer."""
        self.end_time = time.time()
        return self.end_time
    
    def get_elapsed_time(self):
        """
        Get total elapsed time in seconds.
        
        Returns:
            float: Total seconds elapsed, or None if timer not started/stopped
        """
        if self.start_time is None or self.end_time is None:
            return None
        
        return self.end_time - self.start_time
    
    def get_elapsed_time_formatted(self):
        """
        Get elapsed time in human-readable format.
        
        Returns:
            str: Time in format "MM:SS" or "MMm SSs"
        """
        elapsed = self.get_elapsed_time()
        if elapsed is None:
            return None
        
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        if minutes == 0:
            return f"{seconds} sec"
        else:
            return f"{minutes}m {seconds}s"
    
    def calculate_wpm(self, total_spoken_words):
        """
        Calculate Words Per Minute (WPM).
        
        Formula: WPM = Total Spoken Words / Time in Minutes
        
        Args:
            total_spoken_words (int): Total number of words spoken
        
        Returns:
            float: Words per minute, or None if time not recorded
        """
        elapsed = self.get_elapsed_time()
        
        if elapsed is None or elapsed == 0:
            return 0
        
        # Convert elapsed seconds to minutes
        time_in_minutes = elapsed / 60
        
        # Calculate WPM
        wpm = total_spoken_words / time_in_minutes
        
        return round(wpm, 2)
    
    def get_reading_speed_category(self, wpm):
        """
        Categorize reading speed based on WPM.
        
        Args:
            wpm (float): Words per minute
        
        Returns:
            dict: Category information with speed level and interpretation
        """
        if wpm >= 200:
            return {
                'category': 'Very Fast',
                'wpm': wpm,
                'indicator': '⚡ Very fast reading - may indicate skimming',
                'dyslexia_risk': 'Low'
            }
        elif wpm >= 150:
            return {
                'category': 'Fast',
                'wpm': wpm,
                'indicator': '👍 Good reading speed',
                'dyslexia_risk': 'Low'
            }
        elif wpm >= 120:
            return {
                'category': 'Average',
                'wpm': wpm,
                'indicator': '📍 Normal reading speed',
                'dyslexia_risk': 'Low'
            }
        elif wpm >= 90:
            return {
                'category': 'Slightly Slow',
                'wpm': wpm,
                'indicator': '⏱️ Slightly below average - may need focus areas',
                'dyslexia_risk': 'Medium'
            }
        elif wpm >= 60:
            return {
                'category': 'Slow',
                'wpm': wpm,
                'indicator': '⚠️ Slow reading speed - common dyslexia indicator',
                'dyslexia_risk': 'High'
            }
        else:
            return {
                'category': 'Very Slow',
                'wpm': wpm,
                'indicator': '🚩 Very slow reading - strong dyslexia indicator',
                'dyslexia_risk': 'Very High'
            }
    
    def estimate_reading_difficulty(self, wpm, accuracy_percent):
        """
        Estimate reading difficulty based on WPM and accuracy.
        
        Args:
            wpm (float): Words per minute
            accuracy_percent (float): Accuracy percentage (0-100)
        
        Returns:
            dict: Difficulty assessment
        """
        difficulty = {
            'wpm': wpm,
            'accuracy': accuracy_percent,
            'assessment': ''
        }
        
        # Matrix-based assessment
        if accuracy_percent >= 90:
            if wpm >= 120:
                difficulty['assessment'] = "✅ Excellent - Advanced level material"
            else:
                difficulty['assessment'] = "⚠️ Accurate but slow - Consider more familiar material"
        elif accuracy_percent >= 80:
            if wpm >= 120:
                difficulty['assessment'] = "👍 Good - Current level is appropriate"
            else:
                difficulty['assessment'] = "📚 Need more practice at current level"
        elif accuracy_percent >= 70:
            if wpm >= 100:
                difficulty['assessment'] = "📖 Struggling - Try easier material"
            else:
                difficulty['assessment'] = "⚠️ Too difficult - Use easier passages"
        else:
            difficulty['assessment'] = "🚩 Too challenging - Start with simpler material"
        
        return difficulty


def analyze_reading_session(reference_text, spoken_text, elapsed_time):
    """
    Complete reading session analysis combining speed and accuracy.
    
    Args:
        reference_text (str): Original passage
        spoken_text (str): What was recognized
        elapsed_time (float): Time taken in seconds
    
    Returns:
        dict: Complete reading metrics
    """
    analyzer = ReadingSpeedAnalyzer()
    
    # Calculate metrics
    spoken_words = len(spoken_text.split())
    wpm = (spoken_words / elapsed_time) * 60 if elapsed_time > 0 else 0
    
    # Get reading speed category
    speed_category = analyzer.get_reading_speed_category(wpm)
    
    return {
        'elapsed_time_seconds': round(elapsed_time, 2),
        'spoken_words': spoken_words,
        'wpm': round(wpm, 2),
        'speed_category': speed_category['category'],
        'speed_indicator': speed_category['indicator'],
        'dyslexia_risk_wpm': speed_category['dyslexia_risk']
    }


if __name__ == "__main__":
    # Example usage and testing
    print("\n" + "="*70)
    print("📊 READING SPEED ANALYZER - TEST SCENARIOS")
    print("="*70)
    
    # Test Case 1: Average reader
    print("\nTest 1: Average Reader (Normal speed, good accuracy)")
    analyzer = ReadingSpeedAnalyzer()
    analyzer.start_timer()
    time.sleep(2)  # Simulate 2 seconds of reading
    analyzer.stop_timer()
    
    total_words = 40
    elapsed = analyzer.get_elapsed_time()
    wpm = analyzer.calculate_wpm(total_words)
    
    print(f"Total Time: {analyzer.get_elapsed_time_formatted()}")
    print(f"Total Words Spoken: {total_words}")
    print(f"WPM: {wpm}")
    print(f"Category: {analyzer.get_reading_speed_category(wpm)['category']}")
    print(f"Indicator: {analyzer.get_reading_speed_category(wpm)['indicator']}")
    
    # Test Case 2: Slow reader (potential dyslexia)
    print("\n" + "-"*70)
    print("Test 2: Slow Reader (Potential dyslexia indicator)")
    analyzer2 = ReadingSpeedAnalyzer()
    analyzer2.start_timer()
    time.sleep(3)  # Simulate 3 seconds for same words
    analyzer2.stop_timer()
    
    wpm2 = analyzer2.calculate_wpm(total_words)
    print(f"Total Time: {analyzer2.get_elapsed_time_formatted()}")
    print(f"Total Words Spoken: {total_words}")
    print(f"WPM: {wpm2}")
    print(f"Category: {analyzer2.get_reading_speed_category(wpm2)['category']}")
    print(f"Indicator: {analyzer2.get_reading_speed_category(wpm2)['indicator']}")
    print(f"Dyslexia Risk: {analyzer2.get_reading_speed_category(wpm2)['dyslexia_risk']}")
    
    # Test Case 3: Very slow reader
    print("\n" + "-"*70)
    print("Test 3: Very Slow Reader (Strong dyslexia indicator)")
    analyzer3 = ReadingSpeedAnalyzer()
    analyzer3.start_timer()
    time.sleep(4)  # Simulate 4 seconds for same words
    analyzer3.stop_timer()
    
    wpm3 = analyzer3.calculate_wpm(total_words)
    print(f"Total Time: {analyzer3.get_elapsed_time_formatted()}")
    print(f"Total Words Spoken: {total_words}")
    print(f"WPM: {wpm3}")
    print(f"Category: {analyzer3.get_reading_speed_category(wpm3)['category']}")
    print(f"Indicator: {analyzer3.get_reading_speed_category(wpm3)['indicator']}")
    print(f"Dyslexia Risk: {analyzer3.get_reading_speed_category(wpm3)['dyslexia_risk']}")
    
    # Test Case 4: Complete session analysis
    print("\n" + "-"*70)
    print("Test 4: Complete Session Analysis")
    
    reference = "The quick brown fox jumps over the lazy dog"
    spoken = "The quick brown fox jumps over the lazy dog"
    elapsed = 30  # 30 seconds
    
    result = analyze_reading_session(reference, spoken, elapsed)
    print(f"Reference: {reference}")
    print(f"Spoken: {spoken}")
    print(f"\nMetrics:")
    print(f"  Total Time: {result['elapsed_time_seconds']} seconds")
    print(f"  Words Spoken: {result['spoken_words']}")
    print(f"  WPM: {result['wpm']}")
    print(f"  Speed Category: {result['speed_category']}")
    print(f"  Speed Indicator: {result['speed_indicator']}")
    print(f"  Dyslexia Risk (WPM): {result['dyslexia_risk_wpm']}")
    
    # Test Case 5: All WPM categories
    print("\n" + "-"*70)
    print("Test 5: All WPM Categories")
    
    test_wpm_values = [250, 175, 130, 105, 75, 45]
    analyzer_test = ReadingSpeedAnalyzer()
    
    for test_wpm in test_wpm_values:
        category = analyzer_test.get_reading_speed_category(test_wpm)
        print(f"\n  WPM {test_wpm}: {category['category']}")
        print(f"    └─ {category['indicator']}")
        print(f"    └─ Risk Level: {category['dyslexia_risk']}")
    
    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70 + "\n")
