import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './AuthPages.css';

interface LoginPageProps {
  onNavigate?: (page: 'signup' | 'dashboard') => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onNavigate }) => {
  const { login, error, isLoading, clearError } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const errors: Record<string, string> = {};

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    // Validate password
    if (!formData.password) {
      errors.password = 'Password is required';
    }

    return errors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // Clear validation error for this field when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }

    // Clear API error
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    try {
      clearError();
      await login(formData.email, formData.password);
      // Redirect to dashboard on successful login
      onNavigate?.('dashboard');
    } catch {
      // Error is handled and displayed via the error state
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back 👋</h1>
          <p>Sign in to continue your training</p>
        </div>

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              disabled={isLoading}
              autoComplete="email"
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              disabled={isLoading}
              autoComplete="current-password"
            />
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? '⏳ Signing In...' : '✓ Sign In'}
          </button>
        </form>

        {/* Signup Link */}
        <p className="auth-footer">
          Don't have an account?{' '}
          <button
            onClick={() => onNavigate?.('signup')}
            className="auth-link"
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              textDecoration: 'underline',
              cursor: 'pointer',
              padding: 0,
              font: 'inherit'
            }}
          >
            Create one here
          </button>
        </p>

        {/* Demo Account Info */}
        <div className="demo-info">
          <p className="demo-title">Demo Account:</p>
          <p>Email: demo@example.com</p>
          <p>Password: Demo123</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
