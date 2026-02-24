import React from 'react';
import './Loading.css';

interface LoadingProps {
  message?: string;
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Analyzing your reading...' }) => {
  return (
    <div className="loading-container">
      <div className="loading-card">
        <div className="spinner"></div>
        <h2>{message}</h2>
        <p>This may take a few moments</p>
      </div>
    </div>
  );
};
