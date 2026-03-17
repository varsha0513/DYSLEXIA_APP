import React, { useState, useRef, useEffect } from 'react';
import { useMediaRecorder } from '../hooks/useMediaRecorder';
import './EyeFocusWordTracking.css';

interface EyeFocusWordTrackingProps {
  paragraph: string;
  onComplete: (results: EyeFocusResults) => void;
  timePerWordMs?: number; // Speed in milliseconds per word
}

export interface EyeFocusResults {
  originalText: string;
  recognizedText: string;
  correctWords: string[];
  wrongWords: Array<[string, string]>;
  missingWords: string[];
  accuracyPercentage: number;
  totalWords: number;
  correctCount: number;
  wrongCount: number;
  missingCount: number;
}

export const EyeFocusWordTracking: React.FC<EyeFocusWordTrackingProps> = ({
  paragraph,
  onComplete,
  timePerWordMs = 800, // Default to 0.8 seconds
}) => {
  const [state, setState] = useState<'idle' | 'countdown' | 'tracking' | 'results'>('idle');
  const [countdownValue, setCountdownValue] = useState(3);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [results, setResults] = useState<EyeFocusResults | null>(null);
  
  const { startRecording, stopRecording, isRecording, recognizedText, getFinalText } =
    useMediaRecorder();
  
  const words = paragraph.split(/\s+/).filter(w => w.length > 0);
  const countdownIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const trackingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const elapsedTimeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Handle countdown
  useEffect(() => {
    if (state !== 'countdown') return;

    countdownIntervalRef.current = setInterval(() => {
      setCountdownValue(prev => {
        if (prev <= 1) {
          // Start tracking when countdown finishes
          setState('tracking');
          startRecording();
          setCurrentWordIndex(0);
          setElapsedTime(0);
          return 3;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [state, startRecording]);

  // Handle word highlighting during tracking
  useEffect(() => {
    if (state !== 'tracking') return;

    trackingIntervalRef.current = setInterval(() => {
      setCurrentWordIndex(prev => {
        const next = prev + 1;
        if (next >= words.length) {
          // Finished
          return prev;
        }
        return next;
      });
    }, timePerWordMs);

    return () => {
      if (trackingIntervalRef.current) {
        clearInterval(trackingIntervalRef.current);
      }
    };
  }, [state, words.length, timePerWordMs]);

  // Handle elapsed time tracking
  useEffect(() => {
    if (state !== 'tracking') return;

    elapsedTimeIntervalRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1000);
    }, 1000);

    return () => {
      if (elapsedTimeIntervalRef.current) {
        clearInterval(elapsedTimeIntervalRef.current);
      }
    };
  }, [state]);

  // Check if tracking is complete
  useEffect(() => {
    if (state === 'tracking' && currentWordIndex >= words.length - 1) {
      // Stop recording and evaluate
      stopRecording();
      finishTracking();
    }
  }, [currentWordIndex, state, words.length, stopRecording]);

  const handleStartTraining = () => {
    setState('countdown');
    setCountdownValue(3);
  };

  const finishTracking = () => {
    const finalText = getFinalText();
    const evaluationResults = evaluateReadingAccuracy(paragraph, finalText);
    setResults(evaluationResults);
    setState('results');
  };

  const evaluateReadingAccuracy = (original: string, recognized: string): EyeFocusResults => {
    const cleanWord = (word: string) =>
      word.toLowerCase().replace(/[^\w]/g, '');

    const origWords = original.split(/\s+/).filter(w => w.length > 0).map(cleanWord);
    const recWords = recognized.split(/\s+/).filter(w => w.length > 0).map(cleanWord);

    const correctWords: string[] = [];
    const wrongWords: Array<[string, string]> = [];
    const missingWords: string[] = [];

    // Optimized single-pass comparison
    const maxLen = Math.max(origWords.length, recWords.length);
    for (let i = 0; i < maxLen; i++) {
      const origWord = origWords[i];
      const recWord = recWords[i];

      if (!origWord && recWord) {
        continue;
      } else if (origWord && !recWord) {
        missingWords.push(origWord);
      } else if (origWord && recWord) {
        if (origWord === recWord) {
          correctWords.push(origWord);
        } else {
          wrongWords.push([recWord, origWord]);
        }
      }
    }

    const totalWords = origWords.length;
    const correctCount = correctWords.length;
    const wrongCount = wrongWords.length;
    const missingCount = missingWords.length;
    const accuracyPercentage = totalWords > 0 ? Math.round((correctCount / totalWords) * 100) : 0;

    return {
      originalText: original,
      recognizedText: recognized,
      correctWords,
      wrongWords,
      missingWords,
      accuracyPercentage,
      totalWords,
      correctCount,
      wrongCount,
      missingCount,
    };
  };

  const handleRetry = () => {
    setState('idle');
    setCountdownValue(3);
    setCurrentWordIndex(0);
    setElapsedTime(0);
    setResults(null);
  };

  const handleComplete = () => {
    if (results) {
      onComplete(results);
    }
  };

  if (state === 'results' && results) {
    return (
      <div className="eye-focus-container">
        <div className="eye-focus-results">
          <h2 className="results-title">📊 Eye Focus Accuracy Evaluation</h2>

          {/* Accuracy Meter */}
          <div className="accuracy-section">
            <div className="accuracy-meter">
              <div
                className="accuracy-fill"
                style={{
                  width: `${results.accuracyPercentage}%`,
                  backgroundColor:
                    results.accuracyPercentage >= 90
                      ? '#4caf50'
                      : results.accuracyPercentage >= 70
                      ? '#ff9800'
                      : '#e74c3c',
                }}
              />
            </div>
            <div className="accuracy-percentage">{results.accuracyPercentage}% Accurate</div>
          </div>

          {/* Statistics */}
          <div className="stats-grid">
            <div className="stat-card correct">
              <div className="stat-icon">✅</div>
              <div className="stat-value">{results.correctCount}</div>
              <div className="stat-label">Correct Words</div>
            </div>
            <div className="stat-card wrong">
              <div className="stat-icon">❌</div>
              <div className="stat-value">{results.wrongCount}</div>
              <div className="stat-label">Misread Words</div>
            </div>
            <div className="stat-card missing">
              <div className="stat-icon">⏭️</div>
              <div className="stat-value">{results.missingCount}</div>
              <div className="stat-label">Skipped Words</div>
            </div>
            <div className="stat-card total">
              <div className="stat-icon">📝</div>
              <div className="stat-value">{results.totalWords}</div>
              <div className="stat-label">Total Words</div>
            </div>
          </div>

          {/* Misread Words */}
          {results.wrongWords.length > 0 && (
            <div className="feedback-section">
              <h3 className="feedback-title">🔤 Words You Misread</h3>
              <div className="wrong-words-list">
                {results.wrongWords.map((pair, idx) => (
                  <div key={idx} className="word-comparison">
                    <div className="word-said">
                      <span className="label">You said:</span>
                      <span className="word">{pair[0]}</span>
                    </div>
                    <span className="arrow">→</span>
                    <div className="word-correct">
                      <span className="label">Correct:</span>
                      <span className="word">{pair[1]}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Words */}
          {results.missingWords.length > 0 && (
            <div className="feedback-section">
              <h3 className="feedback-title">⏭️ Words You Skipped</h3>
              <div className="missing-words-list">
                {results.missingWords.map((word, idx) => (
                  <span key={idx} className="missing-word">
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recognized vs Original */}
          <div className="text-comparison">
            <div className="comparison-section">
              <h3 className="comparison-title">📖 Original Text</h3>
              <p className="comparison-text">{results.originalText}</p>
            </div>
            <div className="comparison-section">
              <h3 className="comparison-title">🎤 Your Reading</h3>
              <p className="comparison-text">{results.recognizedText || '(No speech recorded)'}</p>
            </div>
          </div>

          {/* Feedback Message */}
          <div className="feedback-message">
            {results.accuracyPercentage >= 90 && (
              <p>🌟 Excellent eye focus! You tracked the words very accurately!</p>
            )}
            {results.accuracyPercentage >= 70 && results.accuracyPercentage < 90 && (
              <p>👍 Good eye focus! Keep practicing to improve further.</p>
            )}
            {results.accuracyPercentage >= 50 && results.accuracyPercentage < 70 && (
              <p>📚 Keep practicing! Focus on tracking each word carefully.</p>
            )}
            {results.accuracyPercentage < 50 && (
              <p>💪 Don't worry! Eye focus training takes practice. Try again!</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="results-actions">
            <button className="btn btn-secondary" onClick={handleRetry}>
              🔄 Try Again
            </button>
            <button className="btn btn-primary" onClick={handleComplete}>
              ✓ Continue to Next Step
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="eye-focus-container">
      {/* Instructions */}
      {state === 'idle' && (
        <div className="eye-focus-instructions">
          <div className="instruction-card">
            <h2>👁️ Eye Focus Training</h2>
            <p>In this exercise, you will:</p>
            <ul>
              <li>📍 Follow each word as it highlights on the screen</li>
              <li>🎤 Read the paragraph aloud while tracking the words</li>
              <li>📊 Receive feedback on your eye focus accuracy</li>
            </ul>
            <p className="instruction-note">
              Keep your eyes on the screen and read clearly into your microphone.
            </p>
            <button className="btn btn-primary btn-large" onClick={handleStartTraining}>
              🚀 Start Training
            </button>
          </div>
        </div>
      )}

      {/* Countdown */}
      {state === 'countdown' && (
        <div className="countdown-section">
          <div className="countdown-display">
            <div className="countdown-number">{countdownValue}</div>
            {countdownValue === 0 && <div className="countdown-go">GO!</div>}
          </div>
          <p className="countdown-text">Get ready to read...</p>
        </div>
      )}

      {/* Word Tracking */}
      {state === 'tracking' && (
        <div className="tracking-section">
          {/* Recording Indicator */}
          <div className="recording-indicator">
            <div className="recording-dot pulse"></div>
            <span>Recording your speech...</span>
          </div>

          {/* Words Display */}
          <div className="words-display">
            {words.map((word, idx) => (
              <span
                key={idx}
                className={`word ${idx === currentWordIndex ? 'highlighted' : ''} ${
                  idx < currentWordIndex ? 'completed' : ''
                }`}
              >
                {word}
              </span>
            ))}
          </div>

          {/* Progress Bar */}
          <div className="progress-section">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${((currentWordIndex + 1) / words.length) * 100}%` }}
              />
            </div>
            <span className="progress-text">
              {currentWordIndex + 1} / {words.length} words
            </span>
          </div>

          {/* Real-time Recognition */}
          {recognizedText && (
            <div className="recognition-display">
              <p className="recognition-label">📣 Recognizing:</p>
              <p className="recognition-text">{recognizedText}</p>
            </div>
          )}

          {/* Elapsed Time */}
          <div className="elapsed-time">
            ⏱️ {(elapsedTime / 1000).toFixed(1)}s
          </div>
        </div>
      )}
    </div>
  );
};
