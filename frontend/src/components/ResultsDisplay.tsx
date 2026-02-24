import React from 'react';
import { AssessmentResponse } from '../types';
import './ResultsDisplay.css';

interface ResultsDisplayProps {
  results: AssessmentResponse;
  onRestart: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  results,
  onRestart,
}) => {
  const {
    accuracy_metrics,
    speed_metrics,
    risk_assessment,
    accuracy_feedback,
    difficulty_assessment,
    recognized_text,
    reference_text,
  } = results;

  const getRiskColor = (riskLevel: string) => {
    const level = riskLevel.toLowerCase();
    if (level.includes('low') || level.includes('minimal')) return '#4caf50';
    if (level.includes('moderate') || level.includes('medium')) return '#ff9800';
    return '#e74c3c';
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 90) return '#4caf50';
    if (accuracy >= 80) return '#8bc34a';
    if (accuracy >= 70) return '#ffc107';
    return '#e74c3c';
  };

  return (
    <div className="results-container">
      <div className="results-card">
        <h1>✅ Assessment Complete!</h1>

        {/* Main Metrics */}
        <div className="metrics-grid">
          {/* Accuracy */}
          <div className="metric-card">
            <div className="metric-value" style={{ color: getAccuracyColor(accuracy_metrics.accuracy_percent) }}>
              {accuracy_metrics.accuracy_percent.toFixed(1)}%
            </div>
            <div className="metric-label">Accuracy</div>
            <div className="metric-detail">
              {accuracy_metrics.correct_words}/{accuracy_metrics.total_words} words correct
            </div>
          </div>

          {/* WPM */}
          <div className="metric-card">
            <div className="metric-value" style={{ color: '#667eea' }}>
              {speed_metrics.wpm.toFixed(0)}
            </div>
            <div className="metric-label">Words Per Minute</div>
            <div className="metric-detail">{speed_metrics.speed_indicator}</div>
          </div>

          {/* Risk Level */}
          <div className="metric-card">
            <div className="metric-value" style={{ color: getRiskColor(risk_assessment.risk_level) }}>
              {risk_assessment.risk_level}
            </div>
            <div className="metric-label">Dyslexia Risk</div>
            <div className="metric-detail">Score: {risk_assessment.risk_score.toFixed(2)}/100</div>
          </div>
        </div>

        {/* Feedback Section */}
        <div className="feedback-section">
          <h2>📊 Detailed Analysis</h2>

          <div className="feedback-item">
            <h3>Performance Feedback</h3>
            <p>{accuracy_feedback}</p>
          </div>

          <div className="feedback-item">
            <h3>Difficulty Assessment</h3>
            <p>{difficulty_assessment}</p>
          </div>

          {/* Accuracy Breakdown */}
          <div className="feedback-item">
            <h3>Word-by-Word Breakdown</h3>
            <div className="accuracy-breakdown">
              <div className="breakdown-item">
                <span className="icon correct">✓</span>
                <strong>{accuracy_metrics.correct_words}</strong> Correct
              </div>
              <div className="breakdown-item">
                <span className="icon" style={{ color: '#ff9800' }}>⚠</span>
                <strong>{accuracy_metrics.wrong_words}</strong> Wrong
              </div>
              <div className="breakdown-item">
                <span className="icon" style={{ color: '#e74c3c' }}>✗</span>
                <strong>{accuracy_metrics.missing_words}</strong> Missing
              </div>
              <div className="breakdown-item">
                <span className="icon" style={{ color: '#2196f3' }}>+</span>
                <strong>{accuracy_metrics.extra_words}</strong> Extra
              </div>
            </div>
          </div>

          {/* Risk Assessment Details */}
          <div className="feedback-item">
            <h3>Risk Assessment Details</h3>
            <p className="risk-summary">{risk_assessment.summary}</p>
            
            {risk_assessment.indicators && risk_assessment.indicators.length > 0 && (
              <div>
                <h4>Indicators:</h4>
                <ul className="indicators-list">
                  {risk_assessment.indicators.map((indicator, idx) => (
                    <li key={idx}>{indicator}</li>
                  ))}
                </ul>
              </div>
            )}

            {risk_assessment.recommendations && risk_assessment.recommendations.length > 0 && (
              <div>
                <h4>Recommendations:</h4>
                <ul className="recommendations-list">
                  {risk_assessment.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Speed Metrics */}
          <div className="feedback-item">
            <h3>Reading Speed Details</h3>
            <div className="speed-details">
              <p><strong>Time:</strong> {speed_metrics.elapsed_time_formatted}</p>
              <p><strong>Words Spoken:</strong> {speed_metrics.spoken_words}</p>
              <p><strong>Speed Category:</strong> {speed_metrics.speed_category}</p>
              <p><strong>Dyslexia Risk (Speed):</strong> {speed_metrics.dyslexia_risk}</p>
            </div>
          </div>

          {/* Text Comparison */}
          <div className="feedback-item">
            <h3>Text Comparison</h3>
            <div className="text-comparison">
              <div className="text-box">
                <h4>Expected:</h4>
                <p>{reference_text}</p>
              </div>
              <div className="text-box">
                <h4>Recognized:</h4>
                <p>{recognized_text}</p>
              </div>
            </div>
          </div>
        </div>

        <button className="btn btn-restart" onClick={onRestart}>
          🔄 Try Another Assessment
        </button>
      </div>
    </div>
  );
};
