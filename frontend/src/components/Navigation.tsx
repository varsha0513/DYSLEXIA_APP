import React from 'react';
import { useTheme } from '../hooks/useTheme';
import './Navigation.css';

export const Navigation: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-icon">🧠</span>
          <span className="logo-text">Dyslexia Assistant</span>
        </div>
        
        <div className="nav-menu">
          <a href="#" className="nav-link">Home</a>
          <a href="#" className="nav-link">Assessment</a>
          <a href="#" className="nav-link">About</a>
        </div>

        <div className="nav-theme">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  );
};
