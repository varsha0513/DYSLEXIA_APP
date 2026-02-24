# DYSLEXIA Assessment Application

A comprehensive Python-based application for assessing reading performance by analyzing reading speed, speech recognition accuracy, and text comparison metrics.

---

## 📋 Completed Tasks

### 1. ✅ Reading Speed Analysis Module
- **File**: `backend/reading_speed.py`
- **Features**:
  - Timer functionality (start/stop) for measuring reading duration
  - Words Per Minute (WPM) calculation based on spoken words and elapsed time
  - Elapsed time formatting (MM:SS format)
  - Reading speed categorization (Very Fast, Fast, Normal, Slow, Very Slow)
  - Dyslexia risk assessment based on WPM thresholds
  - Pause detection and tracking capabilities
  - Performance indicators for different reading speeds

### 2. ✅ Speech Recognition Module
- **File**: `backend/speech_recognition_with_comparison.py`
- **Features**:
  - Vosk-based speech-to-text recognition
  - Real-time audio input capture using SoundDevice
  - Recognition result processing and validation
  - Integration with text comparison module
  - Performance feedback generation
  - Comprehensive reading test execution with results reporting

### 3. ✅ Text Comparison & Accuracy Analysis Module
- **File**: `backend/text_comparison.py`
- **Features**:
  - Text normalization (lowercase conversion, punctuation removal)
  - Sequence matching algorithm using SequenceMatcher
  - Detailed word-by-word comparison metrics:
    - Correct words count
    - Wrong/incorrect words count
    - Missing words (skipped) count
    - Extra words (additional) count
  - Accuracy percentage calculation
  - Performance feedback system based on accuracy:
    - 90%+: Excellent
    - 80-89%: Good
    - 70-79%: Nice effort
    - 60-69%: Keep practicing
    - Below 60%: Practice more

### 4. ✅ Complete Reading Assessment Module
- **File**: `backend/complete_reading_assessment.py`
- **Features**:
  - Integrated reading assessment combining:
    - Speech recognition
    - Text accuracy analysis
    - Reading speed measurement
  - Comprehensive reporting with:
    - Reference and recognized text comparison
    - Reading speed metrics (time, WPM, speed category)
    - Accuracy metrics (correct/wrong/missing/extra words)
    - Combined performance score
    - Detailed feedback and recommendations
  - Support for custom reading passages
  - User-friendly formatted output with progress indicators

### 8. ✅ Dyslexia Risk Scoring System
- **File**: `backend/dyslexia_risk_scoring.py`
- **Features**:
  - Weighted risk score calculation (0-100)
  - Combines all metrics into single risk assessment:
    - WPM (Words Per Minute) - 40% weight
    - Accuracy Percentage - 25% weight
    - Missing Words - 15% weight
    - Wrong Words - 15% weight
    - Extra Words - 5% weight
  - Three-tier risk classification:
    - 🟢 Low Risk (0-30): No major concerns
    - 🟡 Moderate Risk (31-60): Some improvement needed
    - 🔴 High Risk (61+): Professional assessment recommended
  - Component-level scoring breakdown
  - Comprehensive indicator identification
  - Personalized recommendations based on risk level
  - Detailed reporting and summary statistics

### 9. ✅ Risk Scoring Examples & Test Suite
- **File**: `backend/dyslexia_risk_scoring_examples.py`
- **Features**:
  - 10 different reading scenarios demonstrating risk levels
  - From Excellent Reader to Critical Reader cases
  - Visual demonstrations of scoring and classification
  - Reference metrics for each risk level
  - Impact explanation for each metric
- **Location**: `model/vosk-model-small-en-us-0.15`
- **Features**:
  - Pre-trained English speech recognition model
  - MFCC (Mel-Frequency Cepstral Coefficients) configuration
  - Grammar and language models for English
  - Ready-to-use for real-time speech-to-text conversion

### 7. ✅ Dependencies & Environment Setup
- **File**: `requirements.txt`
- **Installed Packages**:
  - vosk (0.3.45) - Speech recognition
  - sounddevice (0.4.5) - Audio input handling
  - numpy (≥1.19.0) - Numerical computations

---

## 🎯 Core Functionality

### Reading Speed Assessment
- Measures and categorizes reading speed (WPM)
- Identifies slow reading patterns (dyslexia indicator)
- Tracks reading hesitations and pauses

### Speech Recognition
- Real-time audio capture and processing
- Converts spoken words to text
- Handles interruptions and background noise

### Accuracy Analysis
- Compares spoken text with reference text
- Identifies specific word errors, omissions, and additions
- Calculates overall reading accuracy percentage

### Dyslexia Risk Scoring
- Combines all metrics (WPM, accuracy, word errors, pauses)
- Calculates comprehensive risk score (0-100)
- Classifies risk level: Low/Moderate/High
- Identifies concerning indicators
- Provides personalized recommendations
- Generates detailed assessment reports

### Performance Feedback
- Provides personalized feedback based on:
  - Reading speed (WPM)
  - Accuracy percentage
  - Word-level errors
  - Risk score and level
- Suggests areas for improvement
- Recommends intervention strategies

---

## 📊 Assessment Metrics

The application tracks and reports:
- **WPM (Words Per Minute)**: Reading speed measurement
- **Accuracy %**: Percentage of correctly read words
- **Correct Words**: Words read exactly as written
- **Wrong Words**: Incorrectly pronounced or substituted words
- **Missing Words**: Words that were skipped
- **Extra Words**: Additional words spoken
- **Reading Duration**: Total time taken to read passage
- **Speed Category**: Classification (Very Slow, Slow, Normal, Fast, Very Fast)
- **Dyslexia Risk**: Risk assessment based on reading speed
- **Risk Score**: Comprehensive score (0-100) combining all metrics
- **Risk Level**: Classification - Low Risk (0-30), Moderate Risk (31-60), High Risk (61+)
- **Component Scores**: Individual scores for WPM, accuracy, missing words, wrong words
- **Risk Indicators**: Specific concerning patterns identified
- **Recommendations**: Personalized improvement strategies

### Risk Scoring Weights
- WPM Factor: 40% - Slow reading is a strong dyslexia indicator
- Accuracy Factor: 25% - Low accuracy indicates comprehension issues
- Missing Words Factor: 15% - Skipped words indicate attention/processing issues
- Wrong Words Factor: 15% - Pronunciation errors indicate phonetic processing issues
- Extra Words Factor: 5% - Minor impact on overall score

---

## 🔧 Technical Stack

- **Language**: Python 3.x
- **Speech Recognition**: Vosk (Kaldi-based)
- **Audio Processing**: SoundDevice, NumPy
- **Text Analysis**: Sequence Matching, Regex
- **Model**: Pre-trained English language model

---

## ✨ Project Status

All core modules implemented and functional:
- ✅ Reading speed analysis
- ✅ Speech recognition integration
- ✅ Text comparison and accuracy analysis
- ✅ Complete assessment pipeline
- ✅ **Dyslexia Risk Scoring System** (NEW)
  - Weighted formula combining all metrics
  - Three-tier risk classification
  - Component-level scoring
  - Indicator identification
  - Personalized recommendations
- ✅ Performance feedback system
- ✅ Example scripts and tests
- ✅ Model integration

Ready for testing and deployment with comprehensive dyslexia risk assessment!

---

**Last Updated**: February 24, 2026
