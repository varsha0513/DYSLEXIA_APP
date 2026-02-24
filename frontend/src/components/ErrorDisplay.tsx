import React from 'react';
import './ErrorDisplay.css';

interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  return (
    <div className="error-container">
      <div className="error-card">
        <div className="error-icon">❌</div>
        <h1>Something went wrong</h1>
        <p className="error-message">{error}</p>
        <div className="error-suggestions">
          <h3>Troubleshooting steps:</h3>
          <ul>
            <li>✓ Make sure backend server is running: <code>python backend/app.py</code></li>
            <li>✓ Check backend is at <code>http://localhost:8000</code></li>
            <li>✓ Verify microphone is connected and permissions are granted</li>
            <li>✓ Check browser console (F12) for detailed error messages</li>
            <li>✓ Try recording again - speak clearly into the microphone</li>
            <li>✓ Ensure stable internet connection</li>
          </ul>
        </div>
        <button className="btn-retry" onClick={onRetry}>
          🔄 Try Again
        </button>
      </div>
    </div>
  );
};
