/*
ChunkReadingWidget Component for Phrase Training

This component provides an interactive interface for users to practice
reading in phrase chunks (2-4 words) instead of individual words.
Users follow highlighted phrases that advance automatically based on pace.

Features:
- Phrase-based reading with visual dividers
- Real-time progress tracking
- Start/Pause/Resume/Reset controls
- 3-second countdown before training
- Reading speed (WPM) calculation from actual time
- Dyslexia-friendly design with large fonts and clear spacing
*/

import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL, submitChunkReadingResults } from '../api';
import './ChunkReadingWidget.css';

// Types for props
interface ChunkReadingWidgetProps {
  paragraph: string;
  isShowing: boolean;
  onClose?: () => void;
}

// Session data from backend
interface ChunkReadingSession {
  text: string;
  phrases: string[];
  total_phrases: number;
  current_phrase_index: number;
  current_phrase: string | null;
  is_paused: boolean;
  is_completed: boolean;
  session_id: string;
}

interface ChunkReadingStats {
  total_phrases: number;
  current_phrase_index: number;
  phrases_completed: number;
  progress_percent: number;
  is_completed: boolean;
}

interface CompletionResult {
  session_id: string;
  total_phrases: number;
  total_words: number;
  elapsed_time_seconds: number;
  calculated_wpm: number;
  phrases_per_second: number;
  status: string;
  message: string;
}

/**
 * ChunkReadingWidget Component
 * 
 * Provides guided phrase-based reading training with automatic progression.
 * Users follow highlighted phrase chunks to improve reading speed and comprehension.
 */
const ChunkReadingWidget: React.FC<ChunkReadingWidgetProps> = ({
  paragraph,
  isShowing,
  onClose,
}) => {
  // State for training session
  const [sessionId, setSessionId] = useState<string>('');
  const [session, setSession] = useState<ChunkReadingSession | null>(null);
  const [stats, setStats] = useState<ChunkReadingStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [countdown, setCountdown] = useState<number | string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [completionResult, setCompletionResult] = useState<CompletionResult | null>(null);
  const [isSubmittingResults, setIsSubmittingResults] = useState(false);
  
  // Refs for timer management
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const elapsedTimeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Configurable phrase pace (milliseconds per phrase)
  const PHRASE_PACE_MS = 2000; // 2 seconds per phrase

  /**
   * Initialize the training session with the provided paragraph
   */
  const initializeSession = async () => {
    try {
      setIsLoading(true);
      setError('');
      setElapsedTime(0);
      setCompletionResult(null);

      // Validate paragraph
      if (!paragraph || paragraph.trim().length === 0) {
        setError('No text available for chunk reading. Please complete the reading assessment first.');
        setIsLoading(false);
        return;
      }

      // Call backend to prepare the session
      const response = await fetch(`${API_BASE_URL}/chunk-reading/prepare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: paragraph,
          min_phrase_length: 2,
          max_phrase_length: 4,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to prepare session: ${response.statusText}`);
      }

      const data = await response.json();
      setSessionId(data.session_id);

      // Load initial session state
      await loadSessionData(data.session_id);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      console.error('Session initialization error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Load current session data from backend
   */
  const loadSessionData = async (sid: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chunk-reading/session/${sid}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load session: ${response.statusText}`);
      }

      const data: ChunkReadingSession = await response.json();
      setSession(data);

      // Load stats
      const statsResponse = await fetch(
        `${API_BASE_URL}/chunk-reading/stats/${sid}`,
        {
          method: 'GET',
        }
      );

      if (statsResponse.ok) {
        const statsData: ChunkReadingStats = await statsResponse.json();
        setStats(statsData);
      }
    } catch (err) {
      console.error('Failed to load session data:', err);
    }
  };

  /**
   * Perform an action on the session
   */
  const performAction = async (action: string) => {
    if (!sessionId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/chunk-reading/action/${sessionId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to perform action: ${response.statusText}`);
      }

      const data = await response.json();
      const updatedSession: ChunkReadingSession = data.session_data;
      setSession(updatedSession);

      // Update stats
      if (action === 'advance_phrase' && !updatedSession.is_completed) {
        const statsResponse = await fetch(
          `${API_BASE_URL}/chunk-reading/stats/${sessionId}`,
          { method: 'GET' }
        );
        if (statsResponse.ok) {
          setStats(await statsResponse.json());
        }
      }

      // If training is completed, submit results
      if (updatedSession.is_completed && !completionResult) {
        await submitResults();
      }
    } catch (err) {
      console.error('Failed to perform action:', err);
    }
  };

  /**
   * Submit training results to backend
   */
  const submitResults = async () => {
    if (!sessionId || isSubmittingResults) return;

    try {
      setIsSubmittingResults(true);
      console.log(`📤 Submitting results for session ${sessionId}`);
      console.log(`   Elapsed time: ${elapsedTime} seconds`);

      const result = await submitChunkReadingResults(sessionId, elapsedTime);
      setCompletionResult(result);

      console.log('✅ Results submitted successfully:', result);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to submit results';
      console.error('Failed to submit results:', errorMsg);
      setError(errorMsg);
    } finally {
      setIsSubmittingResults(false);
    }
  };

  /**
   * Start countdown before training begins
   */
  const startCountdown = async () => {
    if (countdownRef.current) {
      clearTimeout(countdownRef.current);
    }

    let count = 3;
    setCountdown(count);

    const countdownInterval = setInterval(() => {
      count--;

      if (count === 0) {
        setCountdown('Go!');
      } else if (count < 0) {
        clearInterval(countdownInterval);
        setCountdown(null);

        // Start tracking time
        startTimeRef.current = Date.now();
        setElapsedTime(0);

        // Start the actual training
        performAction('start');
        setIsRunning(true);
      } else {
        setCountdown(count);
      }
    }, 1000);

    countdownRef.current = countdownInterval as any;
  };

  /**
   * Start the training
   */
  const handleStart = async () => {
    await startCountdown();
  };

  /**
   * Pause the training
   */
  const handlePause = async () => {
    setIsRunning(false);
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (elapsedTimeIntervalRef.current) {
      clearInterval(elapsedTimeIntervalRef.current);
      elapsedTimeIntervalRef.current = null;
    }
    await performAction('pause');
  };

  /**
   * Resume the training
   */
  const handleResume = async () => {
    startTimeRef.current = Date.now() - (elapsedTime * 1000);
    await performAction('resume');
    setIsRunning(true);
  };

  /**
   * Reset the training
   */
  const handleReset = async () => {
    setIsRunning(false);
    setElapsedTime(0);
    setCompletionResult(null);
    startTimeRef.current = null;
    
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (elapsedTimeIntervalRef.current) {
      clearInterval(elapsedTimeIntervalRef.current);
      elapsedTimeIntervalRef.current = null;
    }
    
    await performAction('reset');
  };

  /**
   * Advance to the next phrase
   */
  const advancePhrase = async () => {
    if (!session) return;
    await performAction('advance_phrase');
  };

  /**
   * Effect to track elapsed time during training
   */
  useEffect(() => {
    if (!isRunning || !startTimeRef.current) {
      return;
    }

    elapsedTimeIntervalRef.current = setInterval(() => {
      const now = Date.now();
      const elapsed = (now - startTimeRef.current!) / 1000;
      setElapsedTime(elapsed);
    }, 100);

    return () => {
      if (elapsedTimeIntervalRef.current) {
        clearInterval(elapsedTimeIntervalRef.current);
        elapsedTimeIntervalRef.current = null;
      }
    };
  }, [isRunning, startTimeRef]);

  /**
   * Effect to handle automatic phrase advancement during training
   */
  useEffect(() => {
    if (!isRunning || !session) {
      return;
    }

    if (session.is_completed) {
      setIsRunning(false);
      if (elapsedTimeIntervalRef.current) {
        clearInterval(elapsedTimeIntervalRef.current);
        elapsedTimeIntervalRef.current = null;
      }
      return;
    }

    // Set timer to advance to next phrase
    timerRef.current = setTimeout(() => {
      advancePhrase();
    }, PHRASE_PACE_MS);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isRunning, session]);

  /**
   * Cleanup timers on unmount
   */
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      if (countdownRef.current) {
        clearInterval(countdownRef.current as any);
      }
      if (elapsedTimeIntervalRef.current) {
        clearInterval(elapsedTimeIntervalRef.current);
      }
    };
  }, []);

  if (!isShowing) {
    return null;
  }

  if (!session) {
    return (
      <div className="chunk-reading-widget">
        <div className="chunk-reading-container">
          <div className="chunk-reading-header">
            <h2>📖 Chunk Reading (Phrase Training)</h2>
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          </div>

          <div className="chunk-reading-intro">
            <p>
              Improve your reading speed and comprehension by reading in meaningful phrases
              rather than individual words. Follow the highlighted phrases as they advance automatically.
            </p>
            <div className="training-info">
              <div className="info-item">
                <span className="info-label">Phrase Length:</span>
                <span className="info-value">2-4 words per phrase</span>
              </div>
              <div className="info-item">
                <span className="info-label">Training Pace:</span>
                <span className="info-value">{PHRASE_PACE_MS / 1000} seconds per phrase</span>
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {!sessionId ? (
            <button
              className="btn btn-start-training"
              onClick={initializeSession}
              disabled={isLoading}
            >
              {isLoading ? '⏳ Preparing...' : '▶ Start Phrase Training'}
            </button>
          ) : (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Loading training session...</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  const progressPercent =
    (session.current_phrase_index / session.total_phrases) * 100;

  return (
    <div className="chunk-reading-widget">
      <div className="chunk-reading-container">
        {/* Header */}
        <div className="chunk-reading-header">
          <h2>📖 Chunk Reading (Phrase Training)</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Progress Info */}
        <div className="progress-info">
          <div className="phrase-count">
            Phrase {session.current_phrase_index + 1} of {session.total_phrases}
          </div>
          <div className="time-display">
            ⏱️ {elapsedTime.toFixed(1)}s
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        {/* Phrase Display Area */}
        <div className="phrase-display-container">
          <div className="phrases-grid">
            {session.phrases.map((phrase, idx) => (
              <div key={idx} className="phrase-wrapper">
                <div
                  className={`phrase ${
                    idx === session.current_phrase_index ? 'highlight' : ''
                  }`}
                >
                  {phrase}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Current Phrase Emphasis */}
        <div className="current-phrase-display">
          <div className="current-phrase-label">Current Phrase:</div>
          <div className="current-phrase-large">
            {session.current_phrase || ''}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="control-buttons">
          {!isRunning && !session.is_completed ? (
            <button
              className="btn btn-primary btn-start"
              onClick={session.is_paused ? handleResume : handleStart}
              disabled={countdown !== null}
            >
              {session.is_paused ? '▶ Resume' : '▶ Start'}
            </button>
          ) : (
            <button 
              className="btn btn-secondary btn-pause" 
              onClick={handlePause}
              disabled={countdown !== null}
            >
              ⏸ Pause
            </button>
          )}

          <button 
            className="btn btn-secondary btn-reset" 
            onClick={handleReset}
            disabled={countdown !== null}
          >
            ↻ Reset
          </button>
        </div>

        {/* Countdown Overlay */}
        {countdown !== null && (
          <div className="countdown-overlay">
            <div className="countdown-content">
              <div className="countdown-number">
                {countdown}
              </div>
              {countdown === 'Go!' && (
                <div className="countdown-subtext">Get Ready!</div>
              )}
            </div>
          </div>
        )}

        {/* Completion Message */}
        {session.is_completed && (
          <div className="completion-message">
            <div className="completion-icon">🎉</div>
            <h3>Fantastic Work!</h3>
            <p>You've completed the phrase reading training!</p>
            
            {completionResult ? (
              <div className="completion-stats">
                <div className="stat-group">
                  <p>
                    <strong>Phrases Read:</strong> {completionResult.total_phrases}
                  </p>
                  <p>
                    <strong>Total Words:</strong> {completionResult.total_words}
                  </p>
                </div>
                
                <div className="stat-divider"></div>
                
                <div className="stat-group">
                  <p>
                    <strong>Time Elapsed:</strong> {completionResult.elapsed_time_seconds.toFixed(1)} seconds
                  </p>
                  <p style={{ fontSize: '1.3em', color: '#667eea', fontWeight: 'bold', marginTop: '15px' }}>
                    🎯 Reading Speed: <span style={{ color: '#764ba2' }}>{completionResult.calculated_wpm.toFixed(0)} WPM</span>
                  </p>
                  <p style={{ fontSize: '0.95em', color: '#666', marginTop: '10px' }}>
                    ({completionResult.phrases_per_second.toFixed(2)} phrases/second)
                  </p>
                </div>
              </div>
            ) : (
              <div className="completion-stats">
                <p>
                  <strong>Phrases Practiced:</strong> {session.total_phrases}
                </p>
                {stats && (
                  <p>
                    <strong>Average Pace:</strong> {(PHRASE_PACE_MS / 1000).toFixed(1)} seconds per phrase
                  </p>
                )}
              </div>
            )}
            
            {isSubmittingResults && (
              <div style={{ marginTop: '15px', fontSize: '0.9em', color: '#666' }}>
                ⏳ Calculating your reading metrics...
              </div>
            )}
            
            <button 
              className="btn btn-primary" 
              onClick={() => handleReset()}
              style={{ marginTop: '20px' }}
            >
              📚 Try Another Round
            </button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
};

export default ChunkReadingWidget;
