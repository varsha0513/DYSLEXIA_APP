import React, { useState } from 'react';
import { useMediaRecorder } from '../hooks/useMediaRecorder';
import { AudioAura } from './AudioAura';
import './ReadingTask.css';

interface ReadingTaskProps {
  age: number;
  paragraph: string;
  onComplete: (audioBlob: Blob, recognizedText: string) => void;
}

export const ReadingTask: React.FC<ReadingTaskProps> = ({
  age,
  paragraph,
  onComplete,
}) => {
  const { startRecording, stopRecording, isRecording, recognizedText, analyser, getFinalText } =
    useMediaRecorder();
  const [isStarted, setIsStarted] = useState(false);
  const [error, setError] = useState<string>('');

  const handleStartReading = async () => {
    setError('');
    setIsStarted(true);

    try {
      console.log('🎤 Starting audio recording and live recognition...');
      await startRecording();
      console.log('✅ Recording started');
    } catch (err: any) {
      console.error('❌ Recording error:', err);
      setError('Failed to access microphone. Please check: 1) Browser permissions, 2) Microphone is connected, 3) Try a different browser');
      setIsStarted(false);
    }
  };

  const handleStopReading = async () => {
    try {
      console.log('⏹ Stopping recording...');
      const audioBlob = await stopRecording();

      console.log(`✅ Audio blob received: ${(audioBlob.size / 1024).toFixed(2)} KB`);

      if (audioBlob.size === 0) {
        setError('Failed to record audio. Please try again.');
        setIsStarted(false);
        return;
      }

      if (audioBlob.size < 1000) {
        setError('Audio file is too small. Please record for at least a few seconds.');
        setIsStarted(false);
        return;
      }

      // Get the complete final recognized text
      const finalText = getFinalText();
      console.log('🎵 Audio ready, sending to backend...');
      console.log(`🎤 Complete recognized text (${finalText.split(' ').filter(w => w).length} words): "${finalText}"`);
      onComplete(audioBlob, finalText);
    } catch (err: any) {
      console.error('❌ Stop recording error:', err);
      setError(`Failed to stop recording: ${err.message}`);
      setIsStarted(false);
    }
  };

  return (
    <div className="reading-task-container">
      <div className="reading-task-card">
        <div className="task-header">
          <h2>📖 Reading Assessment (Age {age})</h2>
          <p className="instruction">Read the paragraph below aloud clearly</p>
        </div>

        <div className="paragraph-box">
          <p className="paragraph-text">{paragraph}</p>
        </div>

        {isRecording && (
          <div className="aura-section">
            <AudioAura isRecording={isRecording} analyser={analyser} size="large" />
          </div>
        )}

        {recognizedText && (
          <div className="recognition-box">
            <h3>🎤 Live Recognition:</h3>
            <p className="recognized-text">{recognizedText}</p>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}

        <div className="controls">
          {!isStarted ? (
            <button className="btn btn-primary" onClick={handleStartReading}>
              🎤 Start Reading
            </button>
          ) : (
            <>
              <button className="btn btn-danger" onClick={handleStopReading}>
                ⏹ Stop & Submit
              </button>
              {isRecording && (
                <div className="recording-indicator">
                  <span className="dot"></span> Recording...
                </div>
              )}
            </>
          )}
        </div>

        <div className="tips">
          <h4>📝 Instructions:</h4>
          <ul>
            <li>✓ Read the entire paragraph clearly and naturally</li>
            <li>✓ Speak at a normal pace (don't rush)</li>
            <li>✓ Ensure your microphone is working properly</li>
            <li>✓ Minimize background noise for best results</li>
            <li>✓ Keep recording for at least 5-10 seconds</li>
            <li>💡 Tip: Open DevTools (F12) → Console to see detailed logs if there's an error</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
