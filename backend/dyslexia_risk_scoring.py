"""
Dyslexia Risk Scoring System

Combines multiple metrics into a comprehensive risk assessment:
- WPM (Words Per Minute)
- Accuracy Percentage
- Missing Words Count
- Wrong Words Count
- Extra Words Count
- Pause Count

Generates a risk score (0-100) and classifies into:
- Low Risk (0-30)
- Moderate Risk (31-60)
- High Risk (61+)
"""


class DyslexiaRiskScorer:
    """
    Calculates dyslexia risk score based on comprehensive reading metrics.
    """
    
    def __init__(self):
        """
        Initialize the risk scorer with weighted formula parameters.
        
        Weights breakdown:
        - WPM Factor (40%): Slow reading is a strong dyslexia indicator
        - Accuracy Factor (25%): Low accuracy indicates reading comprehension issues
        - Missing Words Factor (15%): Skipped words indicate attention/processing issues
        - Wrong Words Factor (15%): Pronunciation errors indicate phonetic processing issues
        - Extra Words Factor (5%): Minor impact on overall score
        """
        self.wpm_weight = 40
        self.accuracy_weight = 25
        self.missing_words_weight = 15
        self.wrong_words_weight = 15
        self.extra_words_weight = 5
        
        # Reference thresholds for normal reading
        self.normal_wpm = 150  # Average adult reading speed
        self.normal_accuracy = 90  # Target accuracy threshold
    
    def calculate_risk_score(self, wpm, accuracy_percent, missing_words, 
                            wrong_words, extra_words, total_words, pause_count=0):
        """
        Calculate comprehensive dyslexia risk score (0-100).
        
        Args:
            wpm (float): Words per minute reading speed
            accuracy_percent (float): Accuracy percentage (0-100)
            missing_words (int): Count of skipped/missing words
            wrong_words (int): Count of incorrectly read words
            extra_words (int): Count of additional words spoken
            total_words (int): Total words in reference text
            pause_count (int, optional): Number of pauses during reading
        
        Returns:
            dict: Comprehensive risk assessment including:
                - risk_score: Final score (0-100)
                - risk_level: Low/Moderate/High Risk
                - component_scores: Individual metric scores
                - indicators: List of concerning indicators
                - recommendations: Personalized recommendations
        """
        
        # Validate inputs
        if total_words == 0:
            return self._create_empty_assessment()
        
        # Calculate component scores
        wpm_score = self._calculate_wpm_score(wpm)
        accuracy_score = self._calculate_accuracy_score(accuracy_percent)
        missing_words_score = self._calculate_missing_words_score(missing_words, total_words)
        wrong_words_score = self._calculate_wrong_words_score(wrong_words, total_words)
        extra_words_score = self._calculate_extra_words_score(extra_words)
        pause_score = self._calculate_pause_score(pause_count)
        
        # Calculate weighted risk score
        total_score = (
            (wpm_score * self.wpm_weight / 100) +
            (accuracy_score * self.accuracy_weight / 100) +
            (missing_words_score * self.missing_words_weight / 100) +
            (wrong_words_score * self.wrong_words_weight / 100) +
            (extra_words_score * self.extra_words_weight / 100)
        )
        
        # Normalize to 0-100 scale
        risk_score = round(min(100, max(0, total_score)))
        
        # Determine risk level
        risk_level = self._classify_risk_level(risk_score)
        
        # Identify concerning indicators
        indicators = self._identify_indicators(
            wpm, accuracy_percent, missing_words, wrong_words, 
            extra_words, total_words, pause_count
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, indicators)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'component_scores': {
                'wpm_score': round(wpm_score, 2),
                'accuracy_score': round(accuracy_score, 2),
                'missing_words_score': round(missing_words_score, 2),
                'wrong_words_score': round(wrong_words_score, 2),
                'extra_words_score': round(extra_words_score, 2),
                'pause_score': round(pause_score, 2)
            },
            'indicators': indicators,
            'recommendations': recommendations,
            'summary': self._generate_summary(risk_score, risk_level, indicators)
        }
    
    def _calculate_wpm_score(self, wpm):
        """
        Calculate risk score from WPM (0-100).
        Lower WPM = Higher Risk
        
        Scoring:
        - 150+ WPM: 0 points (Normal)
        - 100-150 WPM: 25-50 points (Slow)
        - 50-100 WPM: 50-75 points (Very Slow)
        - <50 WPM: 100 points (Extremely Slow)
        
        Args:
            wpm (float): Words per minute
        
        Returns:
            float: Risk score component (0-100)
        """
        if wpm >= self.normal_wpm:
            return 0
        elif wpm >= 100:
            # Linear interpolation: 100 WPM = 50 points, 150 WPM = 0 points
            return ((self.normal_wpm - wpm) / (self.normal_wpm - 100)) * 50
        elif wpm >= 50:
            # Linear interpolation: 50 WPM = 75 points, 100 WPM = 50 points
            return 50 + ((100 - wpm) / 50) * 25
        else:
            # Below 50 WPM = Critical
            return 100
    
    def _calculate_accuracy_score(self, accuracy_percent):
        """
        Calculate risk score from accuracy percentage (0-100).
        Lower accuracy = Higher Risk
        
        Scoring:
        - 90%+ accuracy: 0 points (Excellent)
        - 80-89% accuracy: 15-30 points (Good)
        - 70-79% accuracy: 30-50 points (Fair)
        - 60-69% accuracy: 50-75 points (Poor)
        - <60% accuracy: 100 points (Critical)
        
        Args:
            accuracy_percent (float): Accuracy percentage (0-100)
        
        Returns:
            float: Risk score component (0-100)
        """
        if accuracy_percent >= self.normal_accuracy:
            return 0
        elif accuracy_percent >= 80:
            # Linear: 80% = 30, 90% = 0
            return ((self.normal_accuracy - accuracy_percent) / 10) * 30
        elif accuracy_percent >= 70:
            # Linear: 70% = 50, 80% = 30
            return 30 + ((80 - accuracy_percent) / 10) * 20
        elif accuracy_percent >= 60:
            # Linear: 60% = 75, 70% = 50
            return 50 + ((70 - accuracy_percent) / 10) * 25
        else:
            # Below 60% = Critical
            return 100
    
    def _calculate_missing_words_score(self, missing_words, total_words):
        """
        Calculate risk score from missing words (0-100).
        Missing words indicate attention/processing issues.
        
        Scoring:
        - 0-5% missing: 0-20 points
        - 5-15% missing: 20-50 points
        - 15-30% missing: 50-80 points
        - >30% missing: 100 points (Critical)
        
        Args:
            missing_words (int): Count of missing words
            total_words (int): Total reference words
        
        Returns:
            float: Risk score component (0-100)
        """
        if total_words == 0:
            return 0
        
        missing_percent = (missing_words / total_words) * 100
        
        if missing_percent <= 5:
            # 0-5% missing: 0-20 points
            return (missing_percent / 5) * 20
        elif missing_percent <= 15:
            # 5-15% missing: 20-50 points
            return 20 + ((missing_percent - 5) / 10) * 30
        elif missing_percent <= 30:
            # 15-30% missing: 50-80 points
            return 50 + ((missing_percent - 15) / 15) * 30
        else:
            # >30% missing: 100 points
            return 100
    
    def _calculate_wrong_words_score(self, wrong_words, total_words):
        """
        Calculate risk score from wrong words (0-100).
        Wrong words indicate phonetic/processing difficulties.
        
        Scoring similar to missing words:
        - 0-5% wrong: 0-20 points
        - 5-15% wrong: 20-50 points
        - 15-30% wrong: 50-80 points
        - >30% wrong: 100 points (Critical)
        
        Args:
            wrong_words (int): Count of incorrect words
            total_words (int): Total reference words
        
        Returns:
            float: Risk score component (0-100)
        """
        if total_words == 0:
            return 0
        
        wrong_percent = (wrong_words / total_words) * 100
        
        if wrong_percent <= 5:
            return (wrong_percent / 5) * 20
        elif wrong_percent <= 15:
            return 20 + ((wrong_percent - 5) / 10) * 30
        elif wrong_percent <= 30:
            return 50 + ((wrong_percent - 15) / 15) * 30
        else:
            return 100
    
    def _calculate_extra_words_score(self, extra_words):
        """
        Calculate risk score from extra words (0-100).
        Extra words have minimal impact but indicate lack of focus.
        
        Scoring:
        - 0 extra words: 0 points
        - 1-3 extra words: 5 points
        - 4-6 extra words: 10 points
        - 7+ extra words: 20 points
        
        Args:
            extra_words (int): Count of extra/additional words
        
        Returns:
            float: Risk score component (0-100)
        """
        if extra_words == 0:
            return 0
        elif extra_words <= 3:
            return 5
        elif extra_words <= 6:
            return 10
        else:
            return 20
    
    def _calculate_pause_score(self, pause_count):
        """
        Calculate risk score from pause count (0-100).
        Many pauses indicate hesitation and processing difficulties.
        
        Scoring:
        - 0-2 pauses: 0 points (Normal)
        - 3-5 pauses: 15 points (Some hesitation)
        - 6-10 pauses: 30 points (Noticeable hesitation)
        - 11+ pauses: 50 points (Severe hesitation)
        
        Args:
            pause_count (int): Number of pauses during reading
        
        Returns:
            float: Risk score component (0-100)
        """
        if pause_count <= 2:
            return 0
        elif pause_count <= 5:
            return 15
        elif pause_count <= 10:
            return 30
        else:
            return 50
    
    def _classify_risk_level(self, risk_score):
        """
        Classify risk level based on risk score.
        
        Classification:
        - 0-30: Low Risk
        - 31-60: Moderate Risk
        - 61-100: High Risk
        
        Args:
            risk_score (int): Risk score (0-100)
        
        Returns:
            str: Risk level classification
        """
        if risk_score <= 30:
            return "🟢 Low Risk"
        elif risk_score <= 60:
            return "🟡 Moderate Risk"
        else:
            return "🔴 High Risk"
    
    def _identify_indicators(self, wpm, accuracy_percent, missing_words, 
                            wrong_words, extra_words, total_words, pause_count):
        """
        Identify concerning dyslexia indicators.
        
        Args:
            wpm (float): Words per minute
            accuracy_percent (float): Accuracy percentage
            missing_words (int): Missing words count
            wrong_words (int): Wrong words count
            extra_words (int): Extra words count
            total_words (int): Total words
            pause_count (int): Pause count
        
        Returns:
            list: List of concerning indicators
        """
        indicators = []
        
        # Speed indicators
        if wpm < 50:
            indicators.append("🔴 CRITICAL: Extremely slow reading (< 50 WPM)")
        elif wpm < 100:
            indicators.append("⚠️  Very slow reading speed (< 100 WPM)")
        elif wpm < 150:
            indicators.append("⚠️  Slow reading speed (< 150 WPM)")
        
        # Accuracy indicators
        if accuracy_percent < 60:
            indicators.append("🔴 CRITICAL: Very low accuracy (< 60%)")
        elif accuracy_percent < 70:
            indicators.append("⚠️  Low accuracy (60-70%)")
        elif accuracy_percent < 80:
            indicators.append("⚠️  Below target accuracy (70-80%)")
        
        # Missing words indicators
        missing_percent = (missing_words / total_words * 100) if total_words > 0 else 0
        if missing_percent > 30:
            indicators.append("🔴 CRITICAL: Many skipped words (> 30%)")
        elif missing_percent > 15:
            indicators.append("⚠️  Significant word skipping (15-30%)")
        elif missing_percent > 5:
            indicators.append("⚠️  Some words skipped (5-15%)")
        
        # Wrong words indicators
        wrong_percent = (wrong_words / total_words * 100) if total_words > 0 else 0
        if wrong_percent > 30:
            indicators.append("🔴 CRITICAL: Many pronunciation errors (> 30%)")
        elif wrong_percent > 15:
            indicators.append("⚠️  Significant pronunciation issues (15-30%)")
        elif wrong_percent > 5:
            indicators.append("⚠️  Some pronunciation errors (5-15%)")
        
        # Pause indicators
        if pause_count > 10:
            indicators.append("⚠️  Many pauses detected (> 10 pauses)")
        elif pause_count > 5:
            indicators.append("⚠️  Frequent hesitation (6-10 pauses)")
        
        # Extra words indicator
        if extra_words > 6:
            indicators.append("⚠️  Many extra words (possible reduced focus)")
        
        return indicators if indicators else ["✅ No significant concerns detected"]
    
    def _generate_recommendations(self, risk_level, indicators):
        """
        Generate personalized recommendations based on risk level.
        
        Args:
            risk_level (str): Risk classification
            indicators (list): List of identified indicators
        
        Returns:
            list: List of actionable recommendations
        """
        recommendations = []
        
        if "Low Risk" in risk_level:
            recommendations.append("✅ Continue current reading practice")
            recommendations.append("🎯 Challenge with more complex texts")
            recommendations.append("📚 Maintain consistent reading habits")
        
        elif "Moderate Risk" in risk_level:
            recommendations.append("📖 Practice with age-appropriate passages")
            recommendations.append("🎯 Focus on accuracy over speed")
            recommendations.append("💪 Use multi-sensory reading techniques")
            recommendations.append("📝 Practice phonetic decoding exercises")
        
        else:  # High Risk
            recommendations.append("🚨 Consider professional dyslexia assessment")
            recommendations.append("👨‍🏫 Work with a reading specialist")
            recommendations.append("📖 Use specialized reading intervention programs")
            recommendations.append("🎧 Try audiobook pairing with text reading")
            recommendations.append("⏱️  Practice with shorter, easier passages first")
            recommendations.append("💡 Use visual aids and color overlays")
        
        # Add specific recommendations based on indicators
        if any("slow reading" in ind.lower() for ind in indicators):
            recommendations.append("⚡ Practice fluency drills and timed reading exercises")
        
        if any("pronunciation" in ind.lower() for ind in indicators):
            recommendations.append("🔤 Focus on phonetic awareness training")
        
        if any("skipped" in ind.lower() for ind in indicators):
            recommendations.append("👀 Use finger tracking or pointer while reading")
        
        return recommendations
    
    def _generate_summary(self, risk_score, risk_level, indicators):
        """
        Generate a summary statement about the overall assessment.
        
        Args:
            risk_score (int): Risk score
            risk_level (str): Risk level
            indicators (list): List of indicators
        
        Returns:
            str: Summary statement
        """
        if risk_score <= 30:
            summary = (
                f"Score: {risk_score}/100 - {risk_level}\n"
                "Reading performance is within normal range with no significant concerns."
            )
        elif risk_score <= 60:
            summary = (
                f"Score: {risk_score}/100 - {risk_level}\n"
                "Some areas of reading need improvement. Regular practice and targeted interventions are recommended."
            )
        else:
            summary = (
                f"Score: {risk_score}/100 - {risk_level}\n"
                "Significant reading difficulties detected. Professional evaluation and specialized intervention may be beneficial."
            )
        
        return summary
    
    def _create_empty_assessment(self):
        """Create an empty assessment when no data available."""
        return {
            'risk_score': 0,
            'risk_level': '◯ No Data',
            'component_scores': {},
            'indicators': ['Insufficient data for assessment'],
            'recommendations': ['Complete a reading assessment first'],
            'summary': 'Unable to calculate risk score without reading data'
        }
    
    def format_assessment_report(self, assessment):
        """
        Format assessment results for display.
        
        Args:
            assessment (dict): Assessment results from calculate_risk_score
        
        Returns:
            str: Formatted report string
        """
        report = []
        report.append("\n" + "="*70)
        report.append("🧠 DYSLEXIA RISK ASSESSMENT REPORT")
        report.append("="*70)
        
        # Risk Score Summary
        report.append("\n" + "─"*70)
        report.append("📊 OVERALL RISK ASSESSMENT")
        report.append("─"*70)
        report.append(f"Risk Score:    {assessment['risk_score']}/100")
        report.append(f"Risk Level:    {assessment['risk_level']}")
        report.append(f"\n{assessment['summary']}")
        
        # Component Scores
        if assessment['component_scores']:
            report.append("\n" + "─"*70)
            report.append("📈 COMPONENT SCORES")
            report.append("─"*70)
            scores = assessment['component_scores']
            report.append(f"WPM Score:             {scores.get('wpm_score', 0)}/100")
            report.append(f"Accuracy Score:        {scores.get('accuracy_score', 0)}/100")
            report.append(f"Missing Words Score:   {scores.get('missing_words_score', 0)}/100")
            report.append(f"Wrong Words Score:     {scores.get('wrong_words_score', 0)}/100")
            report.append(f"Extra Words Score:     {scores.get('extra_words_score', 0)}/100")
            report.append(f"Pause Score:           {scores.get('pause_score', 0)}/100")
        
        # Indicators
        report.append("\n" + "─"*70)
        report.append("🔍 INDICATORS")
        report.append("─"*70)
        for indicator in assessment['indicators']:
            report.append(f"• {indicator}")
        
        # Recommendations
        report.append("\n" + "─"*70)
        report.append("💡 RECOMMENDATIONS")
        report.append("─"*70)
        for rec in assessment['recommendations']:
            report.append(f"• {rec}")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    scorer = DyslexiaRiskScorer()
    
    # Example 1: Normal reader
    print("\n\n--- EXAMPLE 1: Normal Reader ---")
    assessment_1 = scorer.calculate_risk_score(
        wpm=145,
        accuracy_percent=92,
        missing_words=1,
        wrong_words=2,
        extra_words=0,
        total_words=50,
        pause_count=0
    )
    print(scorer.format_assessment_report(assessment_1))
    
    # Example 2: Struggling reader
    print("\n\n--- EXAMPLE 2: Struggling Reader ---")
    assessment_2 = scorer.calculate_risk_score(
        wpm=75,
        accuracy_percent=68,
        missing_words=8,
        wrong_words=6,
        extra_words=2,
        total_words=50,
        pause_count=7
    )
    print(scorer.format_assessment_report(assessment_2))
    
    # Example 3: High risk reader
    print("\n\n--- EXAMPLE 3: High Risk Reader ---")
    assessment_3 = scorer.calculate_risk_score(
        wpm=40,
        accuracy_percent=55,
        missing_words=15,
        wrong_words=10,
        extra_words=5,
        total_words=50,
        pause_count=12
    )
    print(scorer.format_assessment_report(assessment_3))
