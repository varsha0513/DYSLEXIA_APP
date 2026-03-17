import React from 'react';
import { useTheme } from '../hooks/useTheme';
import { useAuth } from '../contexts/AuthContext';
import './Navigation.css';

interface NavigationProps {
  onDashboard?: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({ onDashboard }) => {
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <button className="nav-logo" onClick={onDashboard} style={{ background: 'none', border: 'none', cursor: onDashboard ? 'pointer' : 'default' }}>
          <span className="logo-icon">🧠</span>
          <span className="logo-text">Dyslexia Assistant</span>
        </button>
        
        <div className="nav-menu">
          {isAuthenticated && (
            <>
              <a href="#" className="nav-link" onClick={(e) => { e.preventDefault(); onDashboard?.(); }}>📊 Dashboard</a>
              <button className="nav-link logout-link" onClick={logout} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                📤 Logout
              </button>
            </>
          )}
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
