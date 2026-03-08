/*
SpeedTrainerWidget Component for Guided Pace Reading

This component provides an interactive interface for users to practice
reading at controlled paces (measured in Words Per Minute). Users follow
highlighted words that advance automatically based on the selected speed.

Features:
- Multiple training rounds with progressive speed increases
- Word-by-word highlighting with smooth transitions
- Real-time progress tracking
- Start/Pause/Resume/Reset controls
- Dyslexia-friendly design with large fonts and clear spacing
*/

import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../api';
import './SpeedTrainerWidget.css';

// Types for props
interface SpeedTrainerWidgetProps {
  paragraph: string;
  isShowing: boolean;
  onClose?: () => void;
}

// Session data from backend
interface TrainingSession {
  text: string;
  words: string[];
  total_words: number;
  current_round: number;
  current_word_index: number;
  current_word: string | null;
  is_paused: boolean;
  is_completed: boolean;
  rounds: TrainingRound[];
  session_id: string;
}

interface TrainingRound {
  round_number: number;
  wpm: number;
  interval_ms: number;
  duration_seconds: number;
  status: string;
}

interface SessionStats {
  total_words: number;
  total_rounds: number;
  completed_rounds: number;
  current_round: number;
  total_duration_seconds: number;
  average_wpm: number;
  min_wpm: number;
  max_wpm: number;
  is_completed: boolean;
}

/**
 * SpeedTrainerWidget Component
 * 
 * Provides guided pace reading training with progressive speed increases.
 * Users follow highlighted words that advance at a controlled pace.
 */
const SpeedTrainerWidget: React.FC<SpeedTrainerWidgetProps> = ({
  paragraph,
  isShowing,
  onClose,
}) => {
  // State for training session
  const [sessionId, setSessionId] = useState<string>('');
  const [session, setSession] = useState<TrainingSession | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [countdown, setCountdown] = useState<number | string | null>(null);
  
  // Refs for timer management
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /**
   * Initialize the training session with the provided paragraph
   */
  const initializeSession = async () => {
    try {
      setIsLoading(true);
      setError('');

      // Call backend to prepare the session
      const response = await fetch(`${API_BASE_URL}/speed-trainer/prepare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: paragraph,
          speeds: [60, 75, 90], // Default speeds
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
      const response = await fetch(`${API_BASE_URL}/speed-trainer/session/${sid}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load session: ${response.statusText}`);
      }

      const data: TrainingSession = await response.json();
      setSession(data);

      // Load stats
      const statsResponse = await fetch(
        `${API_BASE_URL}/speed-trainer/stats/${sid}`,
        {
          method: 'GET',
        }
      );

      if (statsResponse.ok) {
        const statsData: SessionStats = await statsResponse.json();
        setStats(statsData);
      }
    } catch (err) {
      console.error('Failed to load session data:', err);
    }
  };

  /**
   * Perform an action on the session (start, pause, resume, reset, advance)
   */
  const performAction = async (action: string) => {
    if (!sessionId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/speed-trainer/action/${sessionId}`,
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
      const updatedSession: TrainingSession = data.session_data;
      setSession(updatedSession);

      // Update stats
      if (action === 'advance_word' && !updatedSession.is_completed) {
        // Continue if not completed
        const statsResponse = await fetch(
          `${API_BASE_URL}/speed-trainer/stats/${sessionId}`,
          { method: 'GET' }
        );
        if (statsResponse.ok) {
          setStats(await statsResponse.json());
        }
      }
    } catch (err) {
      console.error('Failed to perform action:', err);
    }
  };

  /**
   * Start countdown before training begins
   */
  const startCountdown = async () => {
    // Clear any existing countdown
    if (countdownRef.current) {
      clearTimeout(countdownRef.current);
    }

    let count = 3;
    setCountdown(count);

    // Show 3, 2, 1 with 1 second each
    const countdownInterval = setInterval(() => {
      count--;

      if (count === 0) {
        setCountdown('Go!');
      } else if (count < 0) {
        // Countdown complete, hide overlay and start training
        clearInterval(countdownInterval);
        setCountdown(null);

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
    await performAction('pause');
  };

  /**
   * Resume the training
   */
  const handleResume = async () => {
    await performAction('resume');
    setIsRunning(true);
  };

  /**
   * Reset the training
   */
  const handleReset = async () => {
    setIsRunning(false);
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    await performAction('reset');
  };

  /**
   * Advance to the next word
   */
  const advanceWord = async () => {
    if (!session) return;

    await performAction('advance_word');
  };

  /**
   * Effect to handle automatic word advancement during training
   */
  useEffect(() => {
    if (!isRunning || !session) {
      return;
    }

    // Check if training is complete
    if (session.is_completed) {
      setIsRunning(false);
      return;
    }

    // Get current round info
    const currentRound = session.rounds[session.current_round];
    if (!currentRound) {
      return;
    }

    // Set timer to advance to next word
    timerRef.current = setTimeout(() => {
      advanceWord();
    }, currentRound.interval_ms);

    // Cleanup
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isRunning, session]);

  /**
   * Cleanup timer on unmount
   */
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      if (countdownRef.current) {
        clearInterval(countdownRef.current as any);
      }
    };
  }, []);

  if (!isShowing) {
    return null;
  }

  if (!session) {
    return (
      <div className="speed-trainer-widget">
        <div className="speed-trainer-container">
          <div className="speed-trainer-header">
            <h2>🚀 Guided Pace Reading</h2>
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          </div>

          <div className="speed-trainer-intro">
            <p>
              Improve your reading speed with guided practice. Follow the highlighted
              words as they advance automatically. Each round gets progressively faster!
            </p>
            <div className="speed-info">
              <div className="speed-level">Round 1: 60 WPM</div>
              <div className="speed-level">Round 2: 75 WPM</div>
              <div className="speed-level">Round 3: 90 WPM</div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {!sessionId ? (
            <button
              className="btn btn-start-training"
              onClick={initializeSession}
              disabled={isLoading}
            >
              {isLoading ? '⏳ Preparing...' : '▶ Start Training'}
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

  const currentRound = session.rounds[session.current_round];
  const progressPercent =
    (session.current_word_index / session.total_words) * 100;

  return (
    <div className="speed-trainer-widget">
      <div className="speed-trainer-container">
        {/* Header */}
        <div className="speed-trainer-header">
          <h2>🚀 Guided Pace Reading</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Round and WPM Info */}
        <div className="round-info">
          <div className="round-badge">
            Round {session.current_round + 1} of {session.rounds.length}
          </div>
          <div className="wpm-display">
            {currentRound?.wpm} WPM
          </div>
          <div className="interval-display">
            {(currentRound?.interval_ms || 1000) / 1000}s per word
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
          <div className="progress-text">
            Word {session.current_word_index + 1} of {session.total_words}
          </div>
        </div>

        {/* Word Display Area */}
        <div className="text-display-container">
          <div className="text-display">
            {session.words.map((word, idx) => (
              <span
                key={idx}
                className={`word ${
                  idx === session.current_word_index ? 'highlight' : ''
                }`}
              >
                {word}
              </span>
            ))}
          </div>
        </div>

        {/* Current Word Display */}
        <div className="current-word-emphasis">
          <div className="current-word-label">Current Word:</div>
          <div className="current-word-large">
            {session.current_word || ''}
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
            <h3>Great Job!</h3>
            <p>You've completed all training rounds!</p>
            {stats && (
              <div className="completion-stats">
                <p>
                  <strong>Average Speed:</strong> {stats.average_wpm.toFixed(0)} WPM
                </p>
                <p>
                  <strong>Total Duration:</strong>{' '}
                  {Math.round(stats.total_duration_seconds)} seconds
                </p>
                <p>
                  <strong>Words Practiced:</strong> {stats.total_words}
                </p>
              </div>
            )}
            <button className="btn btn-primary" onClick={() => handleReset()}>
              Practice Again
            </button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
};

export default SpeedTrainerWidget;
