import React, { useState, useRef, useEffect } from 'react';
import { useMediaRecorder } from '../hooks/useMediaRecorder';
import './PhraseTrainingWidget.css';

interface PhraseTrainingWidgetProps {
  paragraph: string;
  onComplete: (results: PhraseTrainingResults) => void;
}

export interface PhraseTrainingResults {
  originalText: string;
  recognizedText: string;
  phrases: string[];
  correctPhrases: string[];
  incorrectPhrases: Array<[string, string]>; // [recognized, correct]
  missingPhrases: string[];
  accuracyPercentage: number;
  totalPhrases: number;
  correctCount: number;
  incorrectCount: number;
  missingCount: number;
}

export const PhraseTrainingWidget: React.FC<PhraseTrainingWidgetProps> = ({
  paragraph,
  onComplete,
}) => {
  const [state, setState] = useState<'idle' | 'countdown' | 'training' | 'results' | 'error'>('idle');
  const [countdownValue, setCountdownValue] = useState(3);
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [results, setResults] = useState<PhraseTrainingResults | null>(null);
  const [recordingError, setRecordingError] = useState<string | null>(null);

  const { startRecording, stopRecording, isRecording, recognizedText, getFinalText } =
    useMediaRecorder();

  // Split paragraph into phrases (2-4 words)
  const splitIntoPhrases = (text: string): string[] => {
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const phrases: string[] = [];
    
    for (let i = 0; i < words.length; i += 3) {
      // Take 3 words per phrase (flexible between 2-4)
      const phraseWords = words.slice(i, Math.min(i + 3, words.length));
      phrases.push(phraseWords.join(' '));
    }
    
    return phrases;
  };

  const phrases = splitIntoPhrases(paragraph);
  const phraseDisplayTimeMs = 2500; // 2.5 seconds per phrase

  const countdownIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const trainingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const elapsedTimeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Handle countdown
  useEffect(() => {
    if (state !== 'countdown') return;

    countdownIntervalRef.current = setInterval(() => {
      setCountdownValue(prev => {
        if (prev <= 1) {
          // Start training when countdown finishes
          const startTraining = async () => {
            try {
              setRecordingError(null);
              console.log('🎤 Starting recording and phrases...');
              await startRecording();
              setState('training');
              setCurrentPhraseIndex(0);
              setElapsedTime(0);
            } catch (error) {
              console.error('❌ Failed to start recording:', error);
              const errorMsg = error instanceof Error ? error.message : 'Failed to access microphone. Please check permissions.';
              setRecordingError(`Recording Error: ${errorMsg}`);
              setState('error');
            }
          };
          startTraining();
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

  // Handle phrase highlighting during training
  useEffect(() => {
    if (state !== 'training') return;

    trainingIntervalRef.current = setInterval(() => {
      setCurrentPhraseIndex(prev => {
        const next = prev + 1;
        if (next >= phrases.length) {
          // Finished
          return prev;
        }
        return next;
      });
    }, phraseDisplayTimeMs);

    return () => {
      if (trainingIntervalRef.current) {
        clearInterval(trainingIntervalRef.current);
      }
    };
  }, [state, phrases.length]);

  // Handle elapsed time tracking
  useEffect(() => {
    if (state !== 'training') return;

    elapsedTimeIntervalRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1000);
    }, 1000);

    return () => {
      if (elapsedTimeIntervalRef.current) {
        clearInterval(elapsedTimeIntervalRef.current);
      }
    };
  }, [state]);

  // Check if training is complete
  useEffect(() => {
    if (state !== 'training' || currentPhraseIndex < phrases.length - 1) {
      return;
    }

    // Training is complete - add delay to let user finish speaking, then stop recording
    const delayTimer = setTimeout(() => {
      const completeTraining = async () => {
        try {
          console.log('⏹ Training complete - stopping recording after delay...');
          await stopRecording();
          
          // Give stopRecording time to complete its internal processing
          setTimeout(() => {
            console.log('✅ Recording stopped successfully');
            finishTraining();
          }, 1500); // Wait for Web Speech API to finalize
        } catch (error) {
          console.error('❌ Error stopping recording:', error);
          // Still finish training even if stop fails
          setTimeout(() => {
            finishTraining();
          }, 1500);
        }
      };

      completeTraining();
    }, 2000); // Wait 2 seconds after last phrase for user to finish speaking

    return () => clearTimeout(delayTimer);
  }, [currentPhraseIndex, state, phrases.length, stopRecording]);

  const handleStartTraining = () => {
    setRecordingError(null);
    setState('countdown');
    setCountdownValue(3);
  };

  const finishTraining = () => {
    const finalText = getFinalText();
    const finalRecognized = finalText.trim();
    
    console.log('════════════════════════════════════════');
    console.log('🏁 FINISHING PHRASE TRAINING');
    console.log('════════════════════════════════════════');
    console.log(`📝 Original paragraph:`);
    console.log(`   "${paragraph}"`);
    console.log(`🎤 Recognized text:`);
    console.log(`   "${finalRecognized}"`);
    
    if (!finalRecognized || finalRecognized.length === 0) {
      console.warn('⚠️ WARNING: No text was recognized! User may not have spoken or microphone not working.');
      setRecordingError('No speech detected! The microphone or speech recognition may not be working properly.');
      setState('error');
      return;
    }
    
    const evaluationResults = evaluatePhraseAccuracy(paragraph, finalRecognized);
    
    console.log('📊 Phrase Evaluation:');
    console.log(`   Original phrases (${evaluationResults.totalPhrases}): ${evaluationResults.phrases.join(' | ')}`);
    console.log(`   Correct (${evaluationResults.correctCount}): ${evaluationResults.correctPhrases.join(' | ')}`);
    console.log(`   Incorrect (${evaluationResults.incorrectCount}): ${evaluationResults.incorrectPhrases.map(p => `"${p[0]}" → "${p[1]}"`).join(', ')}`); 
    console.log(`   Missing (${evaluationResults.missingCount}): ${evaluationResults.missingPhrases.join(' | ')}`);
    console.log(`   Accuracy: ${evaluationResults.accuracyPercentage}%`);
    console.log('════════════════════════════════════════');
    
    setResults(evaluationResults);
    setState('results');
  };

  const evaluatePhraseAccuracy = (original: string, recognized: string): PhraseTrainingResults => {
    const originalPhrases = splitIntoPhrases(original);
    const recognizedPhrases = splitIntoPhrases(recognized);

    const cleanPhrase = (phrase: string) =>
      phrase.toLowerCase().replace(/[^\w\s]/g, '').trim();

    const cleanOriginalPhrases = originalPhrases.map(cleanPhrase);
    const cleanRecognizedPhrases = recognizedPhrases.map(cleanPhrase);

    const correctPhrases: string[] = [];
    const incorrectPhrases: Array<[string, string]> = [];
    const missingPhrases: string[] = [];

    // Compare phrase by phrase
    const maxLen = Math.max(cleanOriginalPhrases.length, cleanRecognizedPhrases.length);
    for (let i = 0; i < maxLen; i++) {
      const origPhrase = cleanOriginalPhrases[i];
      const recPhrase = cleanRecognizedPhrases[i];

      if (!origPhrase && recPhrase) {
        // Extra phrase - ignore
      } else if (origPhrase && !recPhrase) {
        missingPhrases.push(originalPhrases[i]);
      } else if (origPhrase && recPhrase) {
        if (origPhrase === recPhrase) {
          correctPhrases.push(originalPhrases[i]);
        } else {
          incorrectPhrases.push([recognizedPhrases[i] || recPhrase, originalPhrases[i]]);
        }
      }
    }

    const totalPhrases = cleanOriginalPhrases.length;
    const correctCount = correctPhrases.length;
    const incorrectCount = incorrectPhrases.length;
    const missingCount = missingPhrases.length;
    const accuracyPercentage = totalPhrases > 0 ? Math.round((correctCount / totalPhrases) * 100) : 0;

    return {
      originalText: original,
      recognizedText: recognized,
      phrases: originalPhrases,
      correctPhrases,
      incorrectPhrases,
      missingPhrases,
      accuracyPercentage,
      totalPhrases,
      correctCount,
      incorrectCount,
      missingCount,
    };
  };

  const handleRetry = () => {
    setState('idle');
    setCountdownValue(3);
    setCurrentPhraseIndex(0);
    setElapsedTime(0);
    setResults(null);
    setRecordingError(null);
  };

  const handleComplete = () => {
    if (results) {
      onComplete(results);
    }
  };

  // Results view
  if (state === 'results' && results) {
    return (
      <div className="phrase-training-container">
        <div className="phrase-training-results">
          <h2 className="results-title">📊 Phrase Training Evaluation</h2>

          {/* Accuracy Meter */}
          <div className="accuracy-section">
            <div className="accuracy-meter">
              <div
                className="accuracy-bar"
                style={{
                  width: `${results.accuracyPercentage}%`,
                  backgroundColor:
                    results.accuracyPercentage >= 80
                      ? '#4caf50'
                      : results.accuracyPercentage >= 60
                      ? '#ff9800'
                      : '#e74c3c',
                }}
              />
            </div>
            <div className="accuracy-text">
              <span className="accuracy-percentage">{results.accuracyPercentage}%</span>
              <span className="accuracy-label">Phrase Accuracy</span>
            </div>
          </div>

          {/* Phrase Breakdown */}
          <div className="phrases-breakdown">
            <h3>Phrase Breakdown</h3>
            <div className="breakdown-stats">
              <div className="stat-item correct">
                <span className="stat-icon">✓</span>
                <span className="stat-label">Correct Phrases</span>
                <span className="stat-value">{results.correctCount}</span>
              </div>
              <div className="stat-item incorrect">
                <span className="stat-icon">⚠</span>
                <span className="stat-label">Incorrect Phrases</span>
                <span className="stat-value">{results.incorrectCount}</span>
              </div>
              <div className="stat-item missing">
                <span className="stat-icon">✗</span>
                <span className="stat-label">Missing Phrases</span>
                <span className="stat-value">{results.missingCount}</span>
              </div>
            </div>
          </div>

          {/* Misread Phrases */}
          {results.incorrectPhrases.length > 0 && (
            <div className="misread-phrases">
              <h3>Phrases to Practice</h3>
              <div className="phrases-list">
                {results.incorrectPhrases.map((pair, idx) => (
                  <div key={idx} className="phrase-item">
                    <div className="phrase-comparison">
                      <div className="recognized">
                        <span className="label">You said:</span>
                        <span className="text">{pair[0] || '(silence)'}</span>
                      </div>
                      <div className="arrow">→</div>
                      <div className="correct">
                        <span className="label">Correct:</span>
                        <span className="text">{pair[1]}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Phrases */}
          {results.missingPhrases.length > 0 && (
            <div className="missing-phrases">
              <h3>Phrases You Missed</h3>
              <div className="phrases-list">
                {results.missingPhrases.map((phrase, idx) => (
                  <div key={idx} className="phrase-item missed">
                    <span className="phrase-text">{phrase}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Text Comparison */}
          <div className="text-comparison">
            <h3>Full Text Comparison</h3>
            <div className="text-boxes">
              <div className="text-box">
                <h4>Expected Phrases:</h4>
                <div className="phrases-display">
                  {results.phrases.map((phrase, idx) => (
                    <span key={idx} className="phrase-badge">
                      {phrase}
                    </span>
                  ))}
                </div>
              </div>
              <div className="text-box">
                <h4>Your Reading:</h4>
                <p>{results.recognizedText || '(No speech detected)'}</p>
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div className="training-feedback">
            <h3>💡 Feedback on Phrase Reading</h3>
            {results.accuracyPercentage >= 80 && (
              <p>Excellent! You're reading phrases naturally and accurately. Keep practicing to maintain this fluency!</p>
            )}
            {results.accuracyPercentage >= 60 && results.accuracyPercentage < 80 && (
              <p>Good! You're making progress with phrase-based reading. Focus on the phrases marked above to improve further.</p>
            )}
            {results.accuracyPercentage < 60 && (
              <p>Keep practicing! Reading in phrases takes practice. Focus on grouping words naturally and reading smoothly.</p>
            )}
          </div>

          {/* Actions */}
          <div className="training-actions">
            <button className="btn-retry" onClick={handleRetry}>
              🔄 Try Again
            </button>
            <button className="btn-continue" onClick={handleComplete}>
              ✓ Continue to Next Step
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Countdown view
  if (state === 'countdown') {
    return (
      <div className="phrase-training-container">
        <div className="countdown-display">
          <div className="countdown-number">{countdownValue}</div>
          <p className="countdown-text">Get ready to read phrases!</p>
        </div>
      </div>
    );
  }

  // Training view
  if (state === 'training') {
    return (
      <div className="phrase-training-container">
        <div className="phrase-training-area">
          <div className="recording-indicator">
            <div className="mic-icon">🎤</div>
            <div className="mic-status">
              <div className="mic-dot"></div>
              <span>Recording...</span>
            </div>
          </div>

          <div className="phrases-display">
            {phrases.map((phrase, idx) => (
              <span
                key={idx}
                className={`phrase-chunk ${idx === currentPhraseIndex ? 'highlighted' : ''} ${
                  idx < currentPhraseIndex ? 'completed' : ''
                }`}
              >
                {phrase}
              </span>
            ))}
          </div>

          <div className="training-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${((currentPhraseIndex + 1) / phrases.length) * 100}%`,
                }}
              />
            </div>
            <span className="progress-text">
              Phrase {currentPhraseIndex + 1} of {phrases.length}
            </span>
          </div>

          <div className="time-display">⏱️ {(elapsedTime / 1000).toFixed(1)}s</div>
        </div>
      </div>
    );
  }

  // Error view
  if (state === 'error') {
    return (
      <div className="phrase-training-container">
        <div className="error-display">
          <div className="error-card">
            <h2>❌ Recording Error</h2>
            <p className="error-message">{recordingError || 'Failed to start recording'}</p>
            <div className="troubleshooting">
              <h3>Troubleshooting Steps:</h3>
              <ul>
                <li>✓ Check if you have allowed microphone access to this browser</li>
                <li>✓ Make sure your microphone is not muted or disconnected</li>
                <li>✓ Try reloading the page and granting permissions again</li>
                <li>✓ Test your microphone in browser settings (chrome://settings/content/microphone)</li>
              </ul>
            </div>
            <button className="btn-retry" onClick={handleRetry}>
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Idle/Start view
  return (
    <div className="phrase-training-container">
      <div className="phrase-training-start">
        <div className="start-card">
          <h2>📖 Phrase Training</h2>
          <p className="instructions">
            You will see phrases (chunks of 2–4 words) highlighted one at a time. Read each phrase aloud naturally, and your speech will be recorded and evaluated.
          </p>

          <div className="preview-section">
            <h3>Phrase Preview:</h3>
            <div className="phrases-preview">
              {phrases.map((phrase, idx) => (
                <span key={idx} className="phrase-badge">{phrase}</span>
              ))}
            </div>
          </div>

          <div className="tips-section">
            <h3>💡 Tips:</h3>
            <ul>
              <li>✓ Read each phrase naturally and smoothly</li>
              <li>✓ Don't pause between phrases</li>
              <li>✓ Maintain a comfortable reading pace</li>
              <li>✓ Speak clearly into your microphone</li>
            </ul>
          </div>

          <button className="btn-start-training" onClick={handleStartTraining}>
            🎤 Start Training
          </button>
        </div>
      </div>
    </div>
  );
};
